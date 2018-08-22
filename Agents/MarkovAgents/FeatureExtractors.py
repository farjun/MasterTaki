import numpy as np
import inspect
from TakiGame.GameLogic.State import PartialStateTwoPlayer
from TakiGame.DeckStuff.Card import SpecialNoColor, SpecialWithColor, Color, Card
from TakiGame.GameLogic.Action import Action
from TakiGame.GameLogic.State import TwoPlayerState
from util import Counter


class FeatureExtractors(object):

    def __init__(self):
        self.feature_list, self.features_names = self.init_method_list(inspect.getmembers(self, predicate=inspect.ismethod))
        self.color_counter = Counter()

    def init_method_list(self, full_method_list):
        feature_list = []
        features_names = []
        for name, method in full_method_list:
            if name.startswith("feature"):
                feature_list.append(method)
                features_names.append(name[len("feature") + 1:])
        return feature_list, features_names

    # def init_extra_variables(self, state, action):
    #     self.color_counter = Counter(
    #         x.get_color() for x in state.get_cur_player_cards() if x.get_color() != Color.NO_COLOR)

    def get_feature_vector(self, state, action):
        # self.init_extra_variables(state,action)
        feature_vector = np.array([feature_score(state, action) for feature_score in self.feature_list], dtype=np.float64)
        return feature_vector/10.0

    def get_features_names(self):
        return self.features_names

    def __len__(self):
        return len(self.feature_list)

    # def feature_is_change_color_exists(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_change_color() else 0

    # def feature_start_with_super_taki(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.begin_with_super_taki() else 0
    #
    # def feature_is_draw_cards(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_draw() else 0

    # def feature_is_change_direction_exists(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_change_direction() else 0

    # def feature_is_king_exists(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_king() else 0

    # def feature_is_plus_exists(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_plus() else 0

    # def feature_is_plus2_exists(self, state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_plus_2() else 0
    #
    # def feature_is_stop_exists(self,  state:PartialStateTwoPlayer, action:Action):
    #     return 1 if action.action_is_stop() else 0

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
        if len(action_cards) > 0 and action_cards[0].get_value() == SpecialWithColor.PLUS and len(action_cards) >= 2:
            return 1
        return 0

    def feature_stop_plus_another_card(self, state: PartialStateTwoPlayer, action: Action):
        # Checks if the action start with a stop and has the length of the action
        action_cards = action.get_cards()
        if len(action_cards) > 0 and action_cards[0].get_value() == SpecialWithColor.STOP and len(action_cards) >= 2:
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

    def feature_plus2_when_opponent_close_to_win(self, state: PartialStateTwoPlayer, action: Action):
        # Check if the opponent is close to winning in and your action is plus 2
        if state.get_other_player_info() < 4:
            if action.action_is_plus_2():
                return 1
            return 0
        return 0

    def feature_finished_color(self, state: PartialStateTwoPlayer, action: Action):
        """if all cards of state in the caller of top card are put down by the action"""
        color = state.get_top_card().get_color()
        f = False
        for card in action.get_cards():
            if card.get_color() == color:
                f = True
        if not f:
            return 0
        c = delete_cards(state.get_cur_player_cards(), action.get_cards())
        for card in c:
            if card.get_color() == color:
                return 0
        return 1

    def feature_have_color(self, state: PartialStateTwoPlayer, action: Action):
        """ have a card with color of top card"""
        color = state.get_top_card().get_color()
        for card in state.get_cur_player_cards():
            if card.get_color() == color:
                return 1
        return 0

    def feature_have_value(self, state: PartialStateTwoPlayer, action: Action):
        """ have a card with value of top card"""
        value = state.get_top_card().get_value()
        for card in state.get_cur_player_cards():
            if card.get_value() == value:
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
        color = state.get_cur_player_cards()[0].get_color()
        no_color_flag = False
        # Deal one hand of one card
        if len(state.get_cur_player_cards()) == 1:
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

    # def feature_has_super_taki_in_hand(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the hand has the card super taki in it"""
    #     get the player hand
        # if action.action_is_draw():
        #     hand = state.get_cur_player_cards()
        # else:
        #     hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for super taki
        # for card in hand:
        #     if card.get_value() == SpecialNoColor.SUPER_TAKI:
        #         return 1
        # return 0

    # def feature_has_king_in_hand(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the hand has the card king in it"""
    #     get the player hand
        # if action.action_is_draw():
        #     hand = state.get_cur_player_cards()
        # else:
        #     hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for king
        # for card in hand:
        #     if card.get_value() == SpecialNoColor.KING:
        #         return 1
        # return 0

    # def feature_has_change_color_in_hand(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the hand has the card change_color in it"""
        # get the player hand
        # if action.action_is_draw():
        #     hand = state.get_cur_player_cards()
        # else:
        #     hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for change color
        # for card in hand:
        #     if card.get_value() == SpecialNoColor.CHANGE_COLOR:
        #         return 1
        # return 0

    # def feature_has_taki_in_hand(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the hand has the card taki in it"""
        # get the player hand
        # if action.action_is_draw():
        #     hand = state.get_cur_player_cards()
        # else:
        #     hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for taki
        # for card in hand:
        #     if card.get_value() == SpecialWithColor.TAKI:
        #         return 1
        # return 0

    # def feature_has_plus2_in_hand(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the hand has the card plus2 in it"""
        # get the player hand
        # if action.action_is_draw():
        #     hand = state.get_cur_player_cards()
        # else:
        #     hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
        # Check for plus2
        # for card in hand:
        #     if card.get_value() == SpecialWithColor.PLUS_2:
        #         return 1
        # return 0

    def feature_has_small_hand(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the player hand is smaller than three"""
        if len(state.get_cur_player_cards()) < 3:
            return 1
        return 0

    # def feature_smaller_hand_than_the_opponent(self, state: PartialStateTwoPlayer, action: Action):
    #     """ Check if the player hand is smaller than his opponent"""
        # if len(state.get_cur_player_cards()) < state.get_other_player_info():
        #     return 1
        # return 0

    def feature_bias(self, state: PartialStateTwoPlayer, action: Action):
        return 1

    def feature_really_change_color(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the change color action has really changed color """
        color = state.get_top_card().get_color()

        if action.action_is_draw():
            return 0
        # Deal with the situation in which action was change_color or that action ended in a change_color card
        if action.get_cards()[-1].get_value() == SpecialNoColor.CHANGE_COLOR:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
            # If the action hasn't ended the game and the use of the change_color hasn't really changed the color
            if len(hand) > 0 and color == action.get_change_color():
                return 0
            return 1
        return 0

    def feature_use_king_when_got_no_other_choice(self, state: PartialStateTwoPlayer, action: Action):
        """ Check if the king is used when the player can't put another card instead"""
        active_color = state.get_top_card().get_color()
        # Deal only action that is king and when the card on top of the pile is a color card
        if action.action_is_king() and active_color != Color.NO_COLOR:
            hand = delete_cards(state.get_cur_player_cards(), action.get_cards())
            # Check if the player has no card to put down
            if color_counter(hand, active_color) == 0 and not find_card(hand, SpecialNoColor.CHANGE_COLOR) and \
                not find_card(hand, SpecialNoColor.SUPER_TAKI):
                return 1
        return 0

    def feature_color_huristic(self, state: PartialStateTwoPlayer, action: Action):
        "uses color huristic that Niv rote"
        return featechr_color_hellper(state, action) / 10

    def feature_num_cards(self, state: PartialStateTwoPlayer, action: Action):
        return float(len(state.get_cur_player_cards()) - len(action.cards_to_put)) / 100

    def feature_this_action_wins(self, state: PartialStateTwoPlayer, action: Action):
        return len(action.cards_to_put) == len(state.get_cur_player_cards())

    def feature_last_card_duplict(self, state: PartialStateTwoPlayer, action: Action):
        if action.action_is_draw():
            return 0
        cards = state.get_cur_player_cards()
        cards_left = delete_cards(cards, action.cards_to_put)
        top_card = action.get_top_card()
        for card1 in cards:
            if card1.get_value() == top_card.get_value() and card1.get_color() != top_card.get_color():
                if color_counter(cards_left, top_card.get_color()) == 0:
                    return 1
                else:
                    return -1
        return 0

    # def feature_chooses_best_color(self, state: PartialStateTwoPlayer, action: Action):
    #     if action.action_is_change_color() or Card(SpecialNoColor.SUPER_TAKI, Color.NO_COLOR) in action.cards_to_put:
    #         cards = state.get_cur_player_cards()
    #         color_counter = {key: 0 for key in [Color.RED, Color.GREEN, Color.BLUE, Color.YELLOW]}
    #         for card in cards:
    #             if card.get_color() !=Color.NO_COLOR:
    #                 color_counter[card.get_color()]+=1
    #         max_colors = [k for k, v in color_counter.items() if v == max(color_counter.values())]
    #         if action.get_change_color() in max_colors:
    #             return 1
    #     return 0







def delete_cards(cards_list, cards):
    c = []
    for card in cards_list:
        if card not in cards:
            c.append(card)
    return c

def find_card(hand, card_type):
    """
    Search the hand for the card
    :param hand: The player current hand
    :param card_type: The type of the card
    :return: True if it was found else False
    """
    for card in hand:
        if card.get_value() == card_type:
            return True
    return False

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

def featechr_color_hellper( state: PartialStateTwoPlayer, action: Action):
    cards = state.get_cur_player_cards()
    if action.action_is_draw():
        return 0
    first_card_color = action.get_cards()[0].color
    last_card_color = action.get_cards()[-1].color

    # If the active color is no-color then the agent wouldn't mind changing the color
    if state.get_top_card().get_color() == Color.NO_COLOR:
        return len(action.get_cards())
    # If the action starts with super taki and ends with the active color
    if action.begin_with_super_taki() and state.get_top_card().get_color() == last_card_color:
        return len(action.get_cards())
    # Count the number of cards that are in the same color as the active color
    counter = 0
    for card in cards:
        if card.color == state.get_top_card().get_color():
            counter += 1

    # return the number of cards that the action encapsulate if the color is the same as the active color
    if counter >= 1:
        if state.get_top_card().get_color() == first_card_color:
            return len(action.get_cards())
        return 0
    else:  # else the agent doesn't mind
        return len(action.get_cards())  # todo maybe just 1