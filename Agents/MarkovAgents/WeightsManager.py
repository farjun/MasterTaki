import numpy as np
import inspect
from TakiGame.GameLogic.State import TwoPlayerState


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

    def feature1(self, state, action):
        return 1 if action.action_is_change_color() else 0

    def feature2(self, state, action):
        return 1 if action.begin_with_super_taki() else 0

    def feature3(self, state, action):
        return 1 if action.action_is_draw() else 0

    def feature4(self, state, action):
        return 1 if action.action_is_change_direction() else 0

    def feature5(self, state, action):
        return 1 if action.action_is_king() else 0

    def feature6(self, state, action):
        return 1 if action.action_is_plus() else 0

    def feature7(self, state, action):
        return 1 if action.action_is_plus_2() else 0

    def feature8(self, state, action):
        return 1 if action.action_is_stop() else 0

    def finished_color(self, state: TwoPlayerState, action):
        """if all cards of state in the caller of top card are put down by the action"""
        coler = state.get_top_card().get_color()
        f= False
        for card in action.get_cards():
            if card.get_color() == coler: f= True
        if not f: return 0
        c= deletCardes(state.get_cur_player_cards(), action.get_cards())
        for card in c:
            if card.get_color() == coler: return 0
        return 1

    def have_color(self, state, action):
        """ have a card with color of top cards"""
        coler = state.get_top_card().get_color()
        for card in state.get_cur_player_cards():
            if card.get_color() == coler:
                return 1
        return 0




w = WeightsManager()
print(w.get_score(None, None))

def deletCardes(cards_list, cards):
    c= []
    for card in cards_list:
        if card not in cards: c.append(card)
    return c