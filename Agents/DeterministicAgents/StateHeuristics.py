

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
        return 1000 #todo not really sure about this
    counter = len([card for card in player_hand if card.color == state.get_top_card().color])
    return (counter/number_of_cards) * 100


def remove_cards_heuristic(state):
    return 1/len(state.get_cur_player_cards()) *100

def color_and_remove_heuristic(state):
    return 0.8 * remove_cards_heuristic(state) + 0.2 * color_heuristic(state)