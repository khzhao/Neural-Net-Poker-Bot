from dependencies import *

import hand_winner as hw

card_to_actual = {
	0: "2",
	1: "3",
	2: "4",
	3: "5",
	4: "6",
	5: "7",
	6: "8",
	7: "9",
	8: "T",
	9: "J",
	10: "Q",
	11: "K",
	12: "A"
}

valid_actions = {"fold", "check", "call", "bet", "raise"}

chipstack = 1000

def card_to_string(cards):
	output = ""
	for card in cards:
		output += card_to_actual[card["value"]] + card["suit"][0]
		output += " "

class Dealer:
	def __init__(self):
		self.deck = set(deepcopy(deck))

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

		self.cards = []
		self.opp_actions = []
		self.predictors = []
		self.chipstack = chipstack

	def receive_info(self, info, type_of_info="Cards"):
		if type_of_info == "Cards":
			self.cards.extend(info)
			self.predictors.append(hw.calculateHandStrength(self.cards, iterations))
		else:
			self.opp_actions.append(info)
			self.predictors.append(action[info])

	def next_move(self):
		opp_strength = 0.5
		our_strength = 0.5
		return "call"


if __name__ == "__main__":
	dealer = Dealer()
	human_bot = HumanBot()

	is_user_small_blind = random.randint(0, 1)
	user_chip_stack = chipstack
	small_blind = 1
	big_blind = 2

	while True:
		curr_pot = 0
		# determine who is small blind for this iteration
		bot_goes_first_after_preflop = is_user_small_blind
		user_cards = dealer.reveal_cards(2)
		bot_cards = dealer.reveal_cards(2)
		human_bot.receive_info(bot_cards, type_of_info="Cards")

		if is_user_small_blind:
			user_chip_stack -= small_blind
			string = "You have {} chip(s). You are the small blind. It's your turn (fold, call, raise): "
			string = string.format(user_chip_stack)
			user_action = input(string)
			while user_action not in valid_actions:
				user_action = input("Not a valid action. Actions are fold, call, raise: ")
			human_bot.receive_info(user_action, type_of_info="Action")
		else:
			user_chip_stack -= big_blind
			string = "You have {} chip(s). You are the big blind. {}. It's your turn (fold, check, raise): "
			bot_move = 
			string = string.format(user_chip_stack)

		
		curr_pot += small_blind + big_blind





