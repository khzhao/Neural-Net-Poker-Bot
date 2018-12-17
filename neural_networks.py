from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
import pickle


def train_and_save_models(X1, y1, X2, y2, X3, y3, X4, y4, X5, y5, X6, y6, X7, y7, X8, y8):
	mlp_preflop_you_first = MLPRegressor()
	mlp_preflop_you_second = MLPRegressor()
	mlp_flop_you_first = MLPRegressor()
	mlp_flop_you_second = MLPRegressor()
	mlp_turn_you_first = MLPRegressor()
	mlp_turn_you_second = MLPRegressor()
	mlp_river_you_first = MLPRegressor()
	mlp_river_you_second = MLPRegressor()

	mlp_preflop_you_first.fit(X1, y1)
	mlp_preflop_you_second.fit(X2, y2)
	mlp_flop_you_first.fit(X3, y3)
	mlp_flop_you_second.fit(X4, y4)
	mlp_turn_you_first.fit(X5, y5)
	mlp_turn_you_second.fit(X6, y6)
	mlp_river_you_first.fit(X7, y7)
	mlp_river_you_second.fit(X8, y8)

	pickle.dump(mlp_preflop_you_first, open("models/mlp_preflop_you_first.sav", 'wb'))
	pickle.dump(mlp_preflop_you_second, open("models/mlp_preflop_you_second.sav", 'wb'))
	pickle.dump(mlp_flop_you_first, open("models/mlp_flop_you_first.sav", 'wb'))
	pickle.dump(mlp_flop_you_second, open("models/mlp_flop_you_second.sav", 'wb'))
	pickle.dump(mlp_turn_you_first, open("models/mlp_turn_you_first.sav", 'wb'))
	pickle.dump(mlp_turn_you_second, open("models/mlp_turn_you_second.sav", 'wb'))
	pickle.dump(mlp_river_you_first, open("models/mlp_river_you_first.sav", 'wb'))
	pickle.dump(mlp_river_you_second, open("models/mlp_river_you_second.sav", 'wb'))


def import_model(filename):
	model = pickle.load(open(filename, 'rb'))
	return model

def train_and_save_decision_model(X1, y1):
	lr = LinearRegression()
	lr.fit(X1, y1)
	pickle.dump(lr, open("models/decision_model.sav", "wb"))