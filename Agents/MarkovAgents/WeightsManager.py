import numpy as np
import inspect
from TakiGame.GameLogic.State import PartialStateTwoPlayer
from TakiGame.DeckStuff.Card import SpecialNoColor, SpecialWithColor, Color
from TakiGame.GameLogic.Action import Action

class WeightsManager(object):
    def __init__(self):
        self.fe = FeatureExtractors()
        self.weights = np.ndarray(len(self.fe))

    def get_score(self, state, action):
        return np.dot(self.weights, self.fe.get_feature_vector(state, action))


class FeatureExtractors(object):

    def __init__(self):
        self.feature_list = self.init_method_list(inspect.getmembers(self, predicate=inspect.ismethod))

    def init_method_list(self, full_method_list):
        feature_list = []
        for name, method in full_method_list:
            if name.startswith("feature"):
                feature_list.append(method)
        return feature_list

    def get_feature_vector(self, state, action):
        feature_vector = np.array([feature_score(state, action) for feature_score in self.feature_list])
        return feature_vector

    def __len__(self):
        return len(self.feature_list)

    def feature_cards_that_end_the_game(self, state:PartialStateTwoPlayer, action:Action):
        # Checks if the last remaining card is a plus
        if len(state.cur_player_cards) == 1:
            card = state.cur_player_cards[0]
            if card == SpecialWithColor.PLUS:
                return 0
        return 1

    def feature_plus_another_card(self, state:PartialStateTwoPlayer, action:Action):
        hand = action.get_cards()
        if hand[0] == SpecialWithColor.PLUS and len(hand) == 2:
            return 1
        return 0

    def feature3(self, state, action):
        print("aaaa")
        return 3

    def feature4(self, state, action):
        print("sssss")
        return 4


w = WeightsManager()
print(w.get_score(None, None))