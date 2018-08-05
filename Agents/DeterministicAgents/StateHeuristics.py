
from TakiGame.DeckStuff.TakiDeck import Deck
from TakiGame.DeckStuff.Card import Number, SpecialNoColor, SpecialWithColor, Color, Card
import numpy as np

weights = {}


def color_heuristic(state):
    """
    Derive the state score by looking at the percentage of the cards
    that are in the same color as the card on top of the pile
    :param state: The current state
    :return: The heuristic score of the state
    """

    player_hand = state.get_cur_player_cards()
    number_of_cards = len(player_hand)
    if number_of_cards == 0:
        return 1000 # todo not really sure about this
    counter = len([card for card in player_hand if card.color == state.get_top_card().color])
    return (counter/number_of_cards) * 100


def remove_cards_heuristic(state):
    return 1/len(state.get_cur_player_cards()) *100


def color_and_remove_heuristic(state):
    return 0.8 * remove_cards_heuristic(state) + 0.2 * color_heuristic(state)


def init_card_weights():
    deck = Deck().cards_deck
    for card in deck:
        if card.number_or_special in Number or card.number_or_special == SpecialWithColor.CHANGE_DIRECTION:
            weights[card] = np.power(2, 2)
        elif card.number_or_special in SpecialWithColor:
            if card.number_or_special == SpecialWithColor.TAKI:
                weights[card] = np.power(2, 13)
            else:
                weights[card] = np.power(2, 8)
        else:
            if card.number_or_special == SpecialNoColor.SUPER_TAKI:
                weights[card] = np.power(2, 13)
            else:
                weights[card] = np.power(2, 9)


def weight_heuristic(state):
    hand = state.get_cur_player_cards()

    top_card = state.get_top_card()
    active_color = top_card.color

    taki_exists = plus2_exists = False
    hand_weight = 0
    for card in hand:
        if card.color == active_color or card.color == Color.NO_COLOR:
            hand_weight += weights[card]
        elif card.number_or_special == top_card.number_or_special:
            hand_weight += weights[card]

        if card.number_or_special == SpecialWithColor.PLUS_2 and card.color == active_color:
            plus2_exists = True
        if card.number_or_special == SpecialNoColor.SUPER_TAKI or \
                (card.number_or_special == SpecialWithColor.TAKI and card.color == active_color):
            taki_exists = True

    if state.get_other_player_info() < 3:
        if plus2_exists:
            return hand_weight + np.power(2, 10)
        else:
            return 0
    if state.get_other_player_info() < len(hand):
        if not taki_exists:
            hand_weight /= 2

    if len(hand) == 1:
        card = hand[0].number_or_special
        if card == SpecialWithColor.STOP or card == SpecialWithColor.PLUS or card == SpecialNoColor.KING:
            return 0

    return hand_weight/np.power(2, len(hand))

init_card_weights()