import numpy as np
import inspect
from TakiGame.GameLogic.State import PartialStateTwoPlayer
from TakiGame.DeckStuff.Card import SpecialNoColor, SpecialWithColor, Color
from TakiGame.GameLogic.Action import Action
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
        feature_vector = np.array([feature_score(state, action) for feature_score in self.feature_list], dtype=np.float64)
        return feature_vector/10.0

    def __len__(self):
        return len(self.feature_list)

    def feature_is_change_color_exists(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_change_color() else 0

    def feature_start_with_super_taki(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.begin_with_super_taki() else 0

    def feature_is_draw_cards(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_draw() else 0

    def feature_is_change_direction_exists(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_change_direction() else 0

    def feature_is_king_exists(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_king() else 0

    def feature_is_plus_exists(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_plus() else 0

    def feature_is_plus2_exists(self, state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_plus_2() else 0

    def feature_is_stop_exists(self,  state:PartialStateTwoPlayer, action:Action):
        return 1 if action.action_is_stop() else 0

    def feature_plus_at_the_end(self, state:PartialStateTwoPlayer, action:Action):
        # Checks if the last remaining card is a plus
        if len(state.cur_player_cards) == 1:
            card = state.cur_player_cards[0]
            if card.get_value() == SpecialWithColor.PLUS:
                return 0
        return 1

    def feature_plus_another_card(self, state:PartialStateTwoPlayer, action: Action):
        # Checks if the action start with a plus and has the length of the action
        action_cards = action.get_cards()
        if len(action_cards) > 0 and action_cards[0].get_value() == SpecialWithColor.PLUS and len(action_cards) == 2:
            return 1
        return 0

    def feature_stop_plus_another_card(self, state: PartialStateTwoPlayer, action: Action):
        # Checks if the action start with a stop and has the length of the action
        action_cards = action.get_cards()
        if len(action_cards) > 0 and action_cards[0].get_value() == SpecialWithColor.STOP and len(action_cards) == 2:
            return 1
        return 0

    def feature_taki_length(self, state: PartialStateTwoPlayer, action:Action):
        # A feature that checks the length of the action if it start with taki
        action_cards = action.get_cards()
        if len(action_cards) > 0 and (action_cards[0].get_value() == SpecialWithColor.TAKI or action_cards[0].get_value() == SpecialNoColor.SUPER_TAKI):
            if len(action_cards) > 4:
                return 1
            elif len(action_cards) > 2:
                return 0.7
            return 0.4
        return 0

    def feature_end_game_plus2(self, state: PartialStateTwoPlayer, action: Action):
        # Check if the opponent is close to winning in and your action is plus 2
        if state.get_other_player_info() == 1:
            if action.action_is_plus_2():
                return 1
            return 0
        return 1

    def feature_finished_color(self, state: PartialStateTwoPlayer, action: Action):
        """if all cards of state in the caller of top card are put down by the action"""
        color = state.get_top_card().get_color()
        f = False
        for card in action.get_cards():
            if card.get_color() == color: f= True
        if not f:
            return 0
        c = delete_cards(state.get_cur_player_cards(), action.get_cards())
        for card in c:
            if card.get_color() == color: return 0
        return 1

    def feature_have_color(self, state: PartialStateTwoPlayer, action: Action):
        """ have a card with color of top cards"""
        color = state.get_top_card().get_color()
        for card in state.get_cur_player_cards():
            if card.get_color() == color:
                return 1
        return 0

    def feature_active_color_after_change_color(self, state: PartialStateTwoPlayer, action: Action):
        """feature that represent the amount of cards the player have that are in the same color as the active color"""
        if action.action_is_draw():
            return 0
        new_active_color = action.get_active_color()
        if (state.get_top_card().get_color() != new_active_color and new_active_color != Color.NO_COLOR) or \
            (state.get_top_card().get_color() == Color.NO_COLOR and action.cards_to_put[-1].get_color() != Color.NO_COLOR):

            # count the cards in the hand that are in the same color as the active color
            hand_after_action = delete_cards(state.get_cur_player_cards(), action.get_cards())
            counter = color_counter(hand_after_action, new_active_color)

            if counter > 2:
                return 1
            elif 0 < counter < 2:
                return 0.5
            else:
                return 0
        return 0

    def feature_active_king(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the action is king and if the top card isn't plus 2"""
        if action.action_is_king() and not state.get_top_card().is_plus_2():
            return 1
        return 0

    def feature_one_color(self, state: PartialStateTwoPlayer, action: Action):
        """Check if all of the cards are in one color"""
        color = state.cur_player_cards[0].get_color()
        no_color_flag = False
        # Deal one hand of one card
        if len(state.cur_player_cards) == 1:
            return 1

        if color == Color.NO_COLOR:
            no_color_flag = True

        hand = state.cur_player_cards[1:]
        for card in hand:
            # Deal with the case of the first being a NO_COLOR
            if no_color_flag and card.get_color() != Color.NO_COLOR:
                no_color_flag = False
                color = card.get_color()
            #  Check if the cards are all in one color
            if card.get_color() != color and card.get_color() != Color.NO_COLOR:
                return 0
        return 1

    def feature_has_super_taki_in_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the hand has the card super taki in it"""
        hand = []
        # get the player hand
        if action.action_is_draw():
            hand = state.get_cur_player_cards()
        else:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for super taki
        for card in hand:
            if card.get_value() == SpecialNoColor.SUPER_TAKI:
                return 1
        return 0

    def feature_has_king_in_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the hand has the card king in it"""
        hand = []
        # get the player hand
        if action.action_is_draw():
            hand = state.get_cur_player_cards()
        else:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for king
        for card in hand:
            if card.get_value() == SpecialNoColor.KING:
                return 1
        return 0

    def feature_has_change_color_in_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the hand has the card change_color in it"""
        hand = []
        # get the player hand
        if action.action_is_draw():
            hand = state.get_cur_player_cards()
        else:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for change color
        for card in hand:
            if card.get_value() == SpecialNoColor.CHANGE_COLOR:
                return 1
        return 0

    def feature_has_taki_in_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the hand has the card taki in it"""
        hand = []
        # get the player hand
        if action.action_is_draw():
            hand = state.get_cur_player_cards()
        else:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for taki
        for card in hand:
            if card.get_value() == SpecialWithColor.TAKI:
                return 1
        return 0

    def feature_has_plus2_in_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the hand has the card plus2 in it"""
        hand = []
        # get the player hand
        if action.action_is_draw():
            hand = state.get_cur_player_cards()
        else:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for plus2
        for card in hand:
            if card.get_value() == SpecialWithColor.PLUS_2:
                return 1
        return 0

    def feature_has_small_hand(self, state: PartialStateTwoPlayer, action: Action):
        if len(state.get_cur_player_cards()) < 3:
            return 1
        return 0

    def feature_smaller_hand_than_the_opponent(self, state: PartialStateTwoPlayer, action: Action):
        if len(state.get_cur_player_cards()) < state.get_other_player_info():
            return 1
        return 0

    def feature_bias(self, state: PartialStateTwoPlayer, action: Action):
        return 1


def delete_cards(cards_list, cards):
    c = []
    for card in cards_list:
        if card not in cards:
            c.append(card)
    return c


def color_counter(hand, active_color):
    """
    Find how many cards the player got in his hand that are in the active color
    :param hand: The cards that are in the player's hand
    :param active_color: The top of the pile color
    :return: A counter
    """
    counter = 0
    for card in hand:
        if card.get_color() == active_color:
            counter += 1
    return counter