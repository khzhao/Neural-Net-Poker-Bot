from dependencies import *

import hand_winner as hw
import neural_networks as NN

card_to_actual = {
	0: "2",
	1: "3",
	2: "4",
	3: "5",
	4: "6",
	5: "7",
	6: "8",
	7: "9",
	8: "10",
	9: "Jack",
	10: "Queen",
	11: "King",
	12: "Ace"
}
def give_readable_cards(cards):# input list of cards (in the form dict), output a string telling a user what the cards are
	readableOutputString = ""
	for card in cards:
		readableOutputString = readableOutputString + " [" + str(card_to_actual[card["value"]])+" of "+card["suit"]+"]"
	return readableOutputString
	
action = {
	"fold": -1,
	"check": 0,
	"call": 1, 
	"bet": 2,
	"raise": 2,
}

chipstack = 1000

def card_to_string(cards):
	output = ""
	for card in cards:
		output += card_to_actual[card["value"]] + card["suit"][0]
		output += " "

class Dealer:
	def __init__(self):
		self.deck = deepcopy(deck)

	def reveal_cards(self, num_cards):
		cards = random.sample(self.deck, num_cards)
		for card in cards:
			self.deck.remove(card)
		return cards

	def new_round(self):
		self.deck = set(deepcopy(deck))

class HumanBot:
	def __init__(self):
		self.models = [None for i in range(8)]
		self.models[0] = NN.import_model("models/mlp_preflop_you_first.sav")
		self.models[1] = NN.import_model("models/mlp_preflop_you_second.sav")
		self.models[2] = NN.import_model("models/mlp_flop_you_first.sav")
		self.models[3] = NN.import_model("models/mlp_flop_you_second.sav")
		self.models[4] = NN.import_model("models/mlp_turn_you_first.sav")
		self.models[5] = NN.import_model("models/mlp_turn_you_second.sav")
		self.models[6] = NN.import_model("models/mlp_river_you_first.sav")
		self.models[7] = NN.import_model("models/mlp_river_you_second.sav")

		self.cards = []# the human_bot's two cards
		self.opp_actions = []
		self.predictors = []
		self.chipstack = chipstack

	def reset_oppactions_and_cards(self):
		self.opp_actions = []
		self.cards = []


	def predict(self, community_cards):# human_bot needs to already have had it's cards updated
		# build predictor
		self.predictors = []
		modelToUse = 0
		if len(self.cards) == 2:
			self.predictors.append(hw.calculateStrengthOfHand(self.cards[0:2]))
			modelToUse = 0
		if len(self.opp_actions) >= 1:
			self.predictors.append(action[self.opp_actions[0]])
			modelToUse = 1
		if len(community_cards) >= 3:
			self.predictors.append(hw.calculateStrengthOfHand(self.cards+community_cards[0:3]))
			modelToUse = 2
		if len(self.opp_actions) >= 2:
			self.predictors.append(action[self.opp_actions[1]])
			modelToUse = 3
		if len(community_cards) >= 4:
			self.predictors.append(hw.calculateStrengthOfHand(self.cards+community_cards[0:4]))
			modelToUse = 4
		if len(self.opp_actions) >= 3:
			self.predictors.append(action[self.opp_actions[2]])
			modelToUse = 5
		if len(community_cards) >= 5:
			self.predictors.append(hw.calculateStrengthOfHand(self.cards+community_cards[0:5]))
			modelToUse = 6
		if len(self.opp_actions) >= 4:
			self.predictors.append(action[self.opp_actions[3]])
			modelToUse = 7
		#print("self.opp_actions is: "+str(self.opp_actions))
		#print("model to use is: "+str(modelToUse))
		#print(self.predictors)
		return(self.models[modelToUse].predict([self.predictors]))

	def decideAnAction(self, community_cards, ourWeight=2, oppWeight=2):# self.cards must be updated
		ourStrength = hw.calculateStrengthOfHand(self.cards)
		oppStrength = self.predict(community_cards)
		mean = ourWeight*float(ourStrength) - oppWeight*float(oppStrength)
		randomDraw = np.random.normal(mean,1,1)#mean, sd, number of draws

		foldThreshold = -1# threshold for doing a wrong action
		raiseThreshold = 1

		if randomDraw < foldThreshold:
			return "call"
		elif randomDraw > raiseThreshold:
			return "raise"
		else:
			return "call"


		return self.models[modelToUse].predict(self.predictors)# maybe need to reshape self.predictors to prevent a warning

	def next_move(self):
		opp_strength = 0.5
		our_strength = 0.5
		return "call"


if __name__ == "__main__":
	human_bot = HumanBot()

	# initialize blinds
	user_small_blind = random.randint(0, 1)
	user_chip_stack = chipstack
	small_blind = 1
	big_blind = 2


	# initialize cards variables
	user_hand = None
	flop = None
	turn = None
	river = None

	pot = 0


	state = "post blinds"
	while True:
		
		if state == "post blinds":
			print("*** WELCOME TO A NEW GAME OF CASTRATION POKER ***")
			# initialize new dealer, complete with new deck of cards!
			dealer = Dealer()
			
			human_bot.reset_oppactions_and_cards()# reset the bot's memory

			pot = 0# reset pot cuz its a new game now
			community_cards = []
			user_small_blind = 1-user_small_blind# switch small blind
			if user_small_blind:
				user_chip_stack -= 1
				human_bot.chipstack -= 2
				pot += 3
				print("You are small blind. Your chipstack is now "+str(user_chip_stack))
			else:
				user_chip_stack -= 2
				human_bot.chipstack -= 1
				pot += 3
				print("You are big blind. Your chipstack is now "+str(user_chip_stack))
			state = "preflop"
			continue

		if state == "preflop":
			if user_small_blind:# user goes first
				
				user_hand = dealer.reveal_cards(2)# deal two cards to user
				human_bot.cards.extend(dealer.reveal_cards(2))# deal two cards to bot

				user_action = input("You were dealt:"+give_readable_cards(user_hand)+". Pot: "+str(pot)+". Choose action (check, bet): ")
				if user_action == "fold":
					human_bot.chipstack += pot
					state = "post blinds"
				if user_action == "bet":
					user_chip_stack -= 2
					pot += 2
					print("You bet 2.")
					human_bot.opp_actions.append("bet")
				else:
					print("You checked.")
					human_bot.opp_actions.append("check")
				
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "fold":
					print("Bot folded.")
					user_chip_stack += pot
					state = "post blinds"
				else:
					print("Bot called.")
					if user_action == "bet":
						human_bot.chipstack -= 2
						pot += 2
					state = "flop"
				

			else:# human_bot goes first
				
				user_hand = dealer.reveal_cards(2)# deal two cards to user
				print("You were dealt:"+give_readable_cards(user_hand)+". Pot: "+str(pot))
				human_bot.cards.extend(dealer.reveal_cards(2))# deal two cards to bot
				
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "raise":
					print("Bot raised 2.")
					human_bot.chipstack -= 2
					pot += 2
				else:
					print("Bot called.")
				
				user_action = input("Pot: "+str(pot)+". Choose action (call, fold): ")
				if user_action == "fold":
					print("You folded")
					human_bot.chipstack += pot
					state = "post blinds"
				else:
					print("You called.")
					if bot_action == "raise":
						user_chip_stack -= 2
						pot += 2
					human_bot.opp_actions.append("call")
					state = "flop"
					
				
				
			
		elif state == "flop":
			# first reveal the flop
			community_cards.extend(dealer.reveal_cards(3))
			print("Flop has been revealed. Community cards are now "+give_readable_cards(community_cards)+
									". The pot is "+str(pot)+".")

			if user_small_blind:# human_bot goes first
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "raise":
					print("Bot raised 4.")
					human_bot.chipstack -= 4
					pot += 4
				else:
					print("Bot checked.")
				
				user_action = input("Pot: "+str(pot)+". Choose action (call, fold): ")
				if user_action == "call":
					print("You called.")
					if bot_action == "raise":
						user_chip_stack -= 4
						pot += 4
					human_bot.opp_actions.append("call")
					state = "turn"
				else:
					print("You folded.")
					human_bot.chipstack += pot
					state = "post blinds"

			else:# user goes first
				user_action = input("Pot: "+str(pot)+". Choose action (bet, check): ")
				if user_action == "bet":
					print("You bet 4.")
					user_chip_stack -= 4
					pot += 4
					human_bot.opp_actions.append("bet")
				else:
					print("You checked.")
					human_bot.opp_actions.append("call")
				
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "call":
					print("Bot called.")
					if user_action == "bet":
						human_bot.chipstack -= 4
						pot += 4
					state = "turn"
				else:
					print("Bot folded. You won "+str(pot)+". Congratulations.")
					user_chip_stack += pot
					state = "post blinds"


		elif state == "turn":
			# first reveal the turn
			community_cards.extend(dealer.reveal_cards(1))
			print("Turn has been revealed. Community cards are now "+give_readable_cards(community_cards)+
									". The pot is "+str(pot)+".")

			if user_small_blind:# human_bot goes first
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "raise":
					print("Bot raised 8.")
					human_bot.chipstack -= 8
					pot += 8
				else:
					print("Bot checked.")
				
				user_action = input("Pot: "+str(pot)+". Choose action (call, fold): ")
				if user_action == "call":
					print("You called.")
					if bot_action == "raise":
						user_chip_stack -= 8
						pot += 8
					human_bot.opp_actions.append("call")
					state = "river"
				else:
					print("You folded.")
					human_bot.chipstack += pot
					state = "post blinds"


			else:# user goes first
				user_action = input("Pot: "+str(pot)+". Choose action (bet, check): ")
				if user_action == "bet":
					print("You bet 8.")
					user_chip_stack -= 8
					pot += 8
					human_bot.opp_actions.append("bet")
				else:
					print("You checked.")
					human_bot.opp_actions.append("call")
				
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "call":
					print("Bot called.")
					if user_action == "bet":
						human_bot.chipstack -= 8
						pot += 8
					state = "river"
				else:
					print("Bot folded. You won "+str(pot)+". Congratulations.")
					user_chip_stack += pot
					state = "post blinds"



		elif state == "river":
			# first reveal the river
			community_cards.extend(dealer.reveal_cards(1))
			print("River has been revealed. Community cards are now "+give_readable_cards(community_cards)+
									". The pot is "+str(pot)+".")

			if user_small_blind:# human_bot goes first
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "raise":
					print("Bot raised 16.")
					human_bot.chipstack -= 16
					pot += 16
				else:
					print("Bot checked.")
				
				user_action = input("Pot: "+str(pot)+". Choose action (call, fold): ")
				if user_action == "call":
					print("You called.")
					if bot_action == "raise":
						user_chip_stack -= 16
						pot += 16
					human_bot.opp_actions.append("call")
					state = "showdown"
				else:
					print("You folded.")
					human_bot.chipstack += pot
					state = "post blinds"


			else:# user goes first
				user_action = input("Pot: "+str(pot)+". Choose action (bet, check): ")
				if user_action == "bet":
					print("You bet 16.")
					user_chip_stack -= 16
					pot += 16
					human_bot.opp_actions.append("bet")
				else:
					print("You checked.")
					human_bot.opp_actions.append("call")
				
				bot_action = human_bot.decideAnAction(community_cards)
				if bot_action == "call":
					print("Bot called.")
					if user_action == "bet":
						human_bot.chipstack -= 16
						pot += 16
					state = "showdown"
				else:
					print("Bot folded. You won "+str(pot)+". Congratulations.")
					user_chip_stack += pot
					state = "post blinds"
			
		

		elif state == "showdown":
			user_wins = 0
			if hw.evaluateWinner(user_hand+community_cards, human_bot.cards+community_cards):
				user_wins = 1
			
			if user_wins == 1:
				user_chip_stack += pot
				print("The bot had "+give_readable_cards(human_bot.cards))
				print("You won the pot of "+str(pot)+". Congratulations. You chipstack is now "+str(user_chip_stack))
				sleep(3)
				state = "post blinds"

			else:
				human_bot.chipstack += pot
				print("The bot had "+give_readable_cards(human_bot.cards))
				print("You lost. You just got castrated by the machine. Your chipstack is now only "+str(user_chip_stack))
				sleep(3)
				state = "post blinds"

