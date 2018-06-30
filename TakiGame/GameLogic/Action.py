from TakiGame.DeckStuff.Card import Card


class Action:
    """
    action class that defines an action in the taki game
    action order is from first (at index 0) to last (at last index)
    """
    def __init__(self, cards_to_put: list(Card), no_op=False):
        self.cards_to_put = cards_to_put
        self.no_op = no_op

    def get_cards(self) -> list(Card):
        return self.cards_to_put

    def action_is_draw(self):
        return self.no_op

    def __iter__(self):
        return self.cards_to_put.__iter__()