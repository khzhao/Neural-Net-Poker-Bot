from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup

from dependencies import *
from content_parser import *

import neural_networks as NN
import hand_winner as hw
import os.path

delimiter = "(*)"
delimiter2 = "@#@"

def parse_contents(contents):
	# get rid of <br/>
	contents = [c for c in contents if c.name != "br"]
	return contents[2:]


class CleverPiggy:
	def __init__(self):
		self.piggy_url = "http://www.cleverpiggy.com/limitbot"
		self.models = [None for i in range(8)]
		self.driver = None
		self.decision_model = None

	# If you have already pre-loaded
	def load_models(self):
		self.models[0] = NN.import_model("models/mlp_preflop_you_first.sav")
		self.models[1] = NN.import_model("models/mlp_preflop_you_second.sav")
		self.models[2] = NN.import_model("models/mlp_flop_you_first.sav")
		self.models[3] = NN.import_model("models/mlp_flop_you_second.sav")
		self.models[4] = NN.import_model("models/mlp_turn_you_first.sav")
		self.models[5] = NN.import_model("models/mlp_turn_you_second.sav")
		self.models[6] = NN.import_model("models/mlp_river_you_first.sav")
		self.models[7] = NN.import_model("models/mlp_river_you_second.sav")

	def train_models(self, games):
		X1, y1 = get_training_np_arrays(games, "HOLE", True)
		X2, y2 = get_training_np_arrays(games, "HOLE", False)
		X3, y3 = get_training_np_arrays(games, "FLOP", True)
		X4, y4 = get_training_np_arrays(games, "FLOP", False)
		X5, y5 = get_training_np_arrays(games, "TURN", True)
		X6, y6 = get_training_np_arrays(games, "TURN", False)
		X7, y7 = get_training_np_arrays(games, "RIVER", True)
		X8, y8 = get_training_np_arrays(games, "RIVER", False)
		NN.train_and_save_models(X1, y1, X2, y2, X3, y3, X4, y4, X5, y5, X6, y6, X7, y7, X8, y8)

	def load_decision_model(self):
		self.decision_model = NN.import_model("models/decision_model.sav")

	def train_decision_model(self):
		file = open("raw_data/decision_data.txt", "r").read()
		entries = file.split(delimiter2)
		rows = [[float(el) for el in entr.split(delimiter)] for entr in entries if len(entr) > 0]
		X = [r[:-1] for r in rows]
		y = [[r[-1]] for r in rows]
		NN.train_and_save_decision_model(np.array(X), np.array(y))

	def predict(self, test_x, time, you_go_first):
		# Find the model that we need to use
		index = action_time[time] - you_go_first - 1
		assert self.models[index] != None

		return self.models[index].predict(test_x)

	def establish_connection(self):
		self.driver = webdriver.Chrome()
		self.driver.get(self.piggy_url)

	def next_move(self, raw_contents):
		recent_game = last_game(raw_contents)
		recent = Game(recent_game)
		recent_as_str = "".join(recent_game)
		predictors = recent.predictors_as_matrix()
		opp_strength = 0.5
		our_strength = 0.5

		if "RIVER" in recent_as_str:
			our_strength = hw.calculateStrengthOfHand(recent.river, iterations)
			first = do_you_go_first(recent_game, "RIVER")
			num_cols = action_time["RIVER"] - first
			opp_strength = self.models[num_cols-1].predict([predictors[:num_cols]])
		elif "TURN" in recent_as_str:
			our_strength = hw.calculateStrengthOfHand(recent.turn, iterations)
			first = do_you_go_first(recent_game, "TURN")
			num_cols = action_time["TURN"] - first
			opp_strength = self.models[num_cols-1].predict([predictors[:num_cols]])
		elif "FLOP" in recent_as_str:
			our_strength = hw.calculateStrengthOfHand(recent.flop, iterations)
			first = do_you_go_first(recent_game, "FLOP")
			num_cols = action_time["FLOP"] - first
			opp_strength = self.models[num_cols-1].predict([predictors[:num_cols]])
		elif "HOLE" in recent_as_str:
			our_strength = hw.calculateStrengthOfHand(recent.preflop, iterations)
			first = do_you_go_first(recent_game, "HOLE")
			num_cols = action_time["HOLE"] - first
			opp_strength = self.models[num_cols-1].predict([predictors[:num_cols]])

		decision_pred = []
		chip_stack = None
		for rec in recent_game:
			if "Seat 1: anonymous (" in rec:
				chip_stack = int(rec.split()[-1][1:-1])
				break
		opp_actions = [recent.preflop_opp, recent.flop_opp, recent.turn_opp, recent.river_opp]
		decision_pred = [our_strength, opp_strength[0], chip_stack]
		decision_pred.extend(opp_actions)

		chosen_action = None
		if os.path.exists("models/decision_model.sav"):
			chosen_action = decision_maker(self.decision_model, [np.array(decision_pred[:-1])])
		else:
		 	chosen_action = decideAnAction(our_strength, opp_strength)

		print("CHOSEN ACTION WAS: ", chosen_action)
		print("OUR HAND STRENGTH WAS: ", our_strength)
		print("OPPONENT ESTIMATED HAND STRENGTH WAS: ", opp_strength[0])
		print("***************")

		if "RIVER" in recent_as_str:
			return chosen_action, decision_pred
		else:
			return chosen_action, []

	def acquire_data(self):
		self.establish_connection()
				# Click something random to start the bot
		self.driver.find_element_by_id("call").click()

		curr = None
		chosen_action = None
		raw_data = open("raw_data/raw_data.txt", "a+")
		decision_data = open("raw_data/decision_data.txt", "a+")
		actions = ["fold", "call", "raise"]
		is_trained = os.path.exists("models/mlp_preflop_you_first.sav")
		is_decision = os.path.exists("models/decision_model.sav")
		if is_trained: self.load_models()
		if is_decision: self.load_decision_model()

		qlearn = []
		try:
			sleep(2)
			while True:
				sleep(7)
				curr = BeautifulSoup(self.driver.page_source)
				infobox = curr.find(id="infobox")
				raw_contents = parse_contents(infobox.contents)
				chosen_action = None
				if not is_trained:
					chosen_action = actions[random.randint(1, 2)]
				else:
					chosen_action, predictors = self.next_move(raw_contents)	
					if len(predictors) != 0: 
						qlearn.append(predictors)
						recent_game = last_game(raw_contents)
						for rec in recent_game:
							if "Cleverpiggy wins the pot" in rec:
								if len(qlearn[-1]) < 6:
									qlearn[-1].append(0)
							elif "anonymous wins the pot" in rec:
								if len(qlearn[-1]) < 6:
									qlearn[-1].append(1)
				self.driver.find_element_by_id(chosen_action).click()

		finally:
			raw_infobox = curr.find(id="infobox")
			infobox = parse_contents(raw_infobox.contents)
			text = delimiter.join(infobox)
			raw_data.write(text)
			raw_data.write(delimiter)
			raw_data.close()


			for q in qlearn:
				q = [str(el) for el in q]
				temp = delimiter.join(q)
				decision_data.write(temp)
				decision_data.write(delimiter2)

			decision_data.close()


if __name__ == "__main__":
	CP = CleverPiggy()

	if input("Would you like to acquire more data? (yes or no): ") == "yes":
		CP.acquire_data()
	else:
		# load from data
		data = open("raw_data/raw_data.txt", "r").read()
		data = data.split(delimiter)
		games = game_division(data)
		print(games)
		CP.train_models(games)
		CP.train_decision_model()

