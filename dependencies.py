import numpy as np
import random
from copy import deepcopy
import math

def sigmoid(x):
  return 1 / (1 + math.exp(-x))

# Number of iterations to simulate your hand strength
# via the Monte Carlo method implemented in
# calculateStrengthOfHand
iterations = 150

# Subject to change, because we may need to standardize the
# values of the predictors of opponent action
action = {
    "fold": -1,
    "check": 0,
    "call": 1, 
    "bet": 2,
    "raise": 2,

    # This is just for bug correcting will not influence action made
    # show is not a valid move it is just to correct bugs
    "show": 0
}

action_time = {
    "HOLE": 2,
    "FLOP": 4,
    "TURN": 6,
    "RIVER": 8
}

deck = [    {"value": 0, "suit": "heart"},
            {"value": 1, "suit": "heart"},
            {"value": 2, "suit": "heart"},
            {"value": 3, "suit": "heart"},
            {"value": 4, "suit": "heart"},
            {"value": 5, "suit": "heart"},
            {"value": 6, "suit": "heart"},
            {"value": 7, "suit": "heart"},
            {"value": 8, "suit": "heart"},
            {"value": 9, "suit": "heart"},
            {"value": 10, "suit": "heart"},
            {"value": 11, "suit": "heart"},
            {"value": 12, "suit": "heart"},
            {"value": 0, "suit": "diamond"},
            {"value": 1, "suit": "diamond"},
            {"value": 2, "suit": "diamond"},
            {"value": 3, "suit": "diamond"},
            {"value": 4, "suit": "diamond"},
            {"value": 5, "suit": "diamond"},
            {"value": 6, "suit": "diamond"},
            {"value": 7, "suit": "diamond"},
            {"value": 8, "suit": "diamond"},
            {"value": 9, "suit": "diamond"},
            {"value": 10, "suit": "diamond"},
            {"value": 11, "suit": "diamond"},
            {"value": 12, "suit": "diamond"},
            {"value": 0, "suit": "spade"},
            {"value": 1, "suit": "spade"},
            {"value": 2, "suit": "spade"},
            {"value": 3, "suit": "spade"},
            {"value": 4, "suit": "spade"},
            {"value": 5, "suit": "spade"},
            {"value": 6, "suit": "spade"},
            {"value": 7, "suit": "spade"},
            {"value": 8, "suit": "spade"},
            {"value": 9, "suit": "spade"},
            {"value": 10, "suit": "spade"},
            {"value": 11, "suit": "spade"},
            {"value": 12, "suit": "spade"},
            {"value": 0, "suit": "club"},
            {"value": 1, "suit": "club"},
            {"value": 2, "suit": "club"},
            {"value": 3, "suit": "club"},
            {"value": 4, "suit": "club"},
            {"value": 5, "suit": "club"},
            {"value": 6, "suit": "club"},
            {"value": 7, "suit": "club"},
            {"value": 8, "suit": "club"},
            {"value": 9, "suit": "club"},
            {"value": 10, "suit": "club"},
            {"value": 11, "suit": "club"},
            {"value": 12, "suit": "club"} ]

lookup_table = {
    "2h": {"value": 0, "suit": "heart"},
    "3h": {"value": 1, "suit": "heart"},
    "4h": {"value": 2, "suit": "heart"},
    "5h": {"value": 3, "suit": "heart"},
    "6h": {"value": 4, "suit": "heart"},
    "7h": {"value": 5, "suit": "heart"},
    "8h": {"value": 6, "suit": "heart"},
    "9h": {"value": 7, "suit": "heart"},
    "Th": {"value": 8, "suit": "heart"},
    "Jh": {"value": 9, "suit": "heart"},
    "Qh": {"value": 10, "suit": "heart"},
    "Kh": {"value": 11, "suit": "heart"},
    "Ah": {"value": 12, "suit": "heart"},
    "2d": {"value": 0, "suit": "diamond"},
    "3d": {"value": 1, "suit": "diamond"},
    "4d": {"value": 2, "suit": "diamond"},
    "5d": {"value": 3, "suit": "diamond"},
    "6d": {"value": 4, "suit": "diamond"},
    "7d": {"value": 5, "suit": "diamond"},
    "8d": {"value": 6, "suit": "diamond"},
    "9d": {"value": 7, "suit": "diamond"},
    "Td": {"value": 8, "suit": "diamond"},
    "Jd": {"value": 9, "suit": "diamond"},
    "Qd": {"value": 10, "suit": "diamond"},
    "Kd": {"value": 11, "suit": "diamond"},
    "Ad": {"value": 12, "suit": "diamond"},
    "2s": {"value": 0, "suit": "spade"},
    "3s": {"value": 1, "suit": "spade"},
    "4s": {"value": 2, "suit": "spade"},
    "5s": {"value": 3, "suit": "spade"},
    "6s": {"value": 4, "suit": "spade"},
    "7s": {"value": 5, "suit": "spade"},
    "8s": {"value": 6, "suit": "spade"},
    "9s": {"value": 7, "suit": "spade"},
    "Ts": {"value": 8, "suit": "spade"},
    "Js": {"value": 9, "suit": "spade"},
    "Qs": {"value": 10, "suit": "spade"},
    "Ks": {"value": 11, "suit": "spade"},
    "As": {"value": 12, "suit": "spade"},
    "2c": {"value": 0, "suit": "club"},
    "3c": {"value": 1, "suit": "club"},
    "4c": {"value": 2, "suit": "club"},
    "5c": {"value": 3, "suit": "club"},
    "6c": {"value": 4, "suit": "club"},
    "7c": {"value": 5, "suit": "club"},
    "8c": {"value": 6, "suit": "club"},
    "9c": {"value": 7, "suit": "club"},
    "Tc": {"value": 8, "suit": "club"},
    "Jc": {"value": 9, "suit": "club"},
    "Qc": {"value": 10, "suit": "club"},
    "Kc": {"value": 11, "suit": "club"},
    "Ac": {"value": 12, "suit": "club"} 
}


def decideAnAction(ourStrength, oppStrength, chipStack=-69, ourWeight=2, oppWeight=2):
    mean = ourWeight*float(ourStrength) - oppWeight*float(oppStrength)
    randomDraw = np.random.normal(mean,1,1)#mean, sd, number of draws

    foldThreshold = -1# threshold for doing a wrong action
    raiseThreshold = 1

    if randomDraw < foldThreshold:
        # Must change later because we are just always calling or raising
        # Must add folding aspect to the game
        return "call"
    elif randomDraw > raiseThreshold:
        return "raise"
    else:
        return "call"


def decision_maker(approx_model, predictors):
    # predictors are our_strength, opp_strength, starting_stack, opponent_actions
    # response is whether we won the hand or not
    # Now we must squash the action_value
    action_value = sigmoid(approx_model.predict(predictors))
    randomDraw = np.random.normal(action_value, 1, 1)
    foldThreshold = -0.5# threshold for doing a wrong action
    raiseThreshold = 1.5

    if randomDraw < foldThreshold:
        # Must change later because we are just always calling or raising
        # Must add folding aspect to the game
        return "fold"
    elif randomDraw > raiseThreshold:
        return "raise"
    else:
        return "call"







