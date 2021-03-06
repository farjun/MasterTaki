from TakiGame.DeckStuff.Card import Color


def color_heuristic(action, game, cards):
    """
    A simple heuristic that quantify action based on the wanting to finish all the cards of the active color
    :param action: A set of cards
    :return: the heuristic cost
    """
    if action.action_is_draw():
        return 0
    first_card_color = action.get_cards()[0].color
    last_card_color = action.get_cards()[-1].color

    # If the active color is no-color then the agent wouldn't mind changing the color
    if game.active_color == Color.NO_COLOR:
        return len(action.get_cards())
    # If the action starts with super taki and ends with the active color
    if action.begin_with_super_taki() and game.active_color == last_card_color:
        return len(action.get_cards())
    # Count the number of cards that are in the same color as the active color
    counter = 0
    for card in cards:
        if card.color == game.active_color:
            counter += 1

    # return the number of cards that the action encapsulate if the color is the same as the active color
    if counter >= 1:
        if game.active_color == first_card_color:
            return len(action.get_cards())
        return 0
    else:  # else the agent doesn't mind
        return len(action.get_cards())


def action_len(action, game, cards):
    return len(action.cards_to_put)


def null_h(action, game, cards):
    return 0