from dependencies import *
import hand_winner as hw

# Subject to change, because we may need to standardize the
# values of the predictors of opponent action
action = {
	"fold": -1,
	"check": 0,
	"call": 1, 
	"bet": 2,
	"raise": 2,
	# This is just for bug correcting will not influence action made
	"show": 0
}

action_time = {
	"HOLE": 2,
	"FLOP": 4,
	"TURN": 6,
	"RIVER": 8
}

# Number of iterations to simulate your hand strength
# via the Monte Carlo method implemented in
# calculateStrengthOfHand
iterations = 150

# Divides the raw content list into list of games played unedited
# raw content list can be obtained from the parse_contents function
def game_division(training):
	games = []
	curr_game = []
	for i in range(len(training)):
		if i < len(training) - 1 and "Full Tilt Poker Game" in training[i+1]:
			curr_game.append(training[i])
			# Test if all times and rounds were performed, can change later
			# from the string to other data structure for performance reasons
			curr_game_as_str = "".join(curr_game)
			if "HOLE" in curr_game_as_str and \
				 "FLOP" in curr_game_as_str and \
				 "TURN" in curr_game_as_str and \
				 "RIVER" in curr_game_as_str and \
				 "Show Down" in curr_game_as_str:
				 games.append(curr_game)
			curr_game = []
		else:
			curr_game.append(training[i])
	return games


def last_game(training):
	backwards = list(reversed(training))
	for i in range(len(backwards)):
		if "Full Tilt Poker Game" in backwards[i]:
			return list(reversed(backwards[:i+1]))
	return []


# Find out whether you are big blind or small blind, game
# is the list of strings of the actions in the game
def is_small_blind(game):
	for el in game:
		if 'Cleverpiggy posts the big blind' in el:
			return True
	return False


# Given the current game and the time in the game
# Outputs whether it is your turn to go first or not
def do_you_go_first(game, time):
	if time == "HOLE" and is_small_blind(game): 
		return True
	elif time != "HOLE" and not is_small_blind(game): 
		return True
	else: 
		return False


# Finds the cards at every time in the game
# @args - time: "HOLE", "FLOP", "TURN", "RIVER"
# Returns list of dictionary format of card instead of string
# "HOLE": gives YOUR cards
# The rest gives the community cards
def find_cards(game, time):
	output = []
	i = 0
	while i < len(game):
		el = game[i]
		if time in el:
			if time == "HOLE": el = game[i+1]
			for card in el.split()[3:]:
				if "[" in card and "]" in card:
					output.append(card[1:-1])
				elif "[" in card:
					output.append(card[1:])
				elif "]" in card:
					output.append(card[:-1])
				else:
					output.append(card)
			break
		i += 1
	return [lookup_table[res] for res in output]


# Finds list of opponent actions at each time
# @args - time: "HOLE", "FLOP", "TURN", "RIVER"
# Returns the action as a string: can be 
# "check", "raise", "fold"
def find_opp_action(game, time):
	i = 0
	while i < len(game):
		el = game[i]
		if time in el:
			i += 1
			while i < len(game):
				el = game[i]
				if "Cleverpiggy" in el:
					return action[el.split()[1][:-1]]
				i += 1
			break
		i += 1
	return 0


# Find opponent hand in the current game
def find_opp_hand(game):
	output = []
	i = 0
	try:
		while i < len(game):
			if "Show Down" in game[i]:
				for card in game[i+1].split()[2:]:
					if "[" in card and "]" in card:
						output.append(card[1:-1])
					elif "[" in card:
						output.append(card[1:])
					elif "]" in card:
						output.append(card[:-1])
					else:
						output.append(card)
			i += 1
		return [lookup_table[res] for res in output]
	except:
		return output


# Current game is given by an index returned from
# the game_division function
class Game:
	def __init__(self, game):
		self.preflop = find_cards(game, "HOLE")
		self.flop = self.preflop + find_cards(game, "FLOP")
		self.turn = self.flop + find_cards(game, "TURN")
		self.river = self.turn + find_cards(game, "RIVER")

		self.preflop_opp = find_opp_action(game, "HOLE")
		self.flop_opp = find_opp_action(game, "FLOP")
		self.turn_opp = find_opp_action(game, "TURN")
		self.river_opp = find_opp_action(game, "RIVER")

		self.opp_hand = find_opp_hand(game) 
		self.is_small_blind = is_small_blind(game)

	def predictors_as_matrix(self):
		predict_vector = []
		predict_vector.append(hw.calculateStrengthOfHand(self.preflop, nSims=iterations))
		predict_vector.append(self.preflop_opp)
		predict_vector.append(hw.calculateStrengthOfHand(self.flop, nSims=iterations))
		predict_vector.append(self.flop_opp)
		predict_vector.append(hw.calculateStrengthOfHand(self.turn, nSims=iterations))
		predict_vector.append(self.turn_opp)
		predict_vector.append(hw.calculateStrengthOfHand(self.river, nSims=iterations))
		predict_vector.append(self.river_opp)
		return predict_vector


# Training is the raw string output from Cleverpiggy
# Must divide into list of games
# Remember to call game_division for list of games later
def filter_games(list_of_games, time, you_go_first):
	games = [Game(el) for el in list_of_games]
	games_small = [el for el in games if el.is_small_blind and len(el.opp_hand) != 0]
	games_big = [el for el in games if not el.is_small_blind and len(el.opp_hand) != 0]

	if time == "HOLE" and you_go_first:
		return games_small
	elif time != "HOLE" and not you_go_first:
		return games_small
	else:
		return games_big


# Get the matrices and predictors, corresponds to the 
# relevant network and model pertaining to the time and
# whether you go first or not
def get_training_np_arrays(list_of_games, time, you_go_first):
	relevent_games = filter_games(list_of_games, time, you_go_first)
	length = len(relevent_games)
	num_col = None

	num_cols = action_time[time] - you_go_first
	X = []
	y = []
	
	for i in range(len(relevent_games)):
		game = relevent_games[i]
		predict_vector = game.predictors_as_matrix()[:num_cols]
		X.append(predict_vector)
		y.append(hw.calculateStrengthOfHand(game.opp_hand, nSims=iterations))

	X = np.array(X)
	y = np.array(y)

	return X, y

		











	







