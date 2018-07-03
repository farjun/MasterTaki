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

    def action_is_stop(self):
        if self.action_is_draw():
            return False
        last_card = self.cards_to_put[-1]
        return last_card.is_stop()

    def action_is_change_direction(self):
        if self.action_is_draw():
            return False
        last_card = self.cards_to_put[-1]
        return last_card.is_change_direction()

    def action_is_plus_2(self):
        if self.action_is_draw():
            return False
        last_card = self.cards_to_put[-1]
        return last_card.is_plus_2()

    def action_is_plus(self):
        if self.action_is_draw():
            return False
        last_card = self.cards_to_put[-1]
        return last_card.is_plus()

    def __iter__(self):
        return self.cards_to_put.__iter__()