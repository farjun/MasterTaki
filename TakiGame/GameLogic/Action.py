from TakiGame.DeckStuff.Card import Color


class Action:
    """
    action class that defines an action in the taki game
    action order is from first (at index 0) to last (at last index)
    """
    def __init__(self, cards_to_put: list, no_op=False, change_color=Color.NO_COLOR):
        self.cards_to_put = cards_to_put
        self.no_op = no_op
        self.change_color = change_color

    def get_cards(self) -> list:
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

    def action_is_king(self):
        if self.action_is_draw():
            return False
        for card in self.cards_to_put:
            if card.is_king():
                return True
        return False

    def action_is_change_color(self):
        if self.action_is_draw():
            return False
        last_card = self.cards_to_put[-1]
        return last_card.is_change_color()

    def get_change_color(self):
        return self.change_color

    def get_active_color(self):
        return self.change_color if self.action_is_change_color() else self.cards_to_put[-1].get_color()

    def get_top_card(self):
        return self.cards_to_put[-1]

    def begin_with_super_taki(self):
        if self.action_is_draw():
            return False
        first_card = self.cards_to_put[0]
        return first_card.is_super_taki()

    def __iter__(self):
        return self.cards_to_put.__iter__()

    def __repr__(self):
        if self.no_op:
            return "Draw Cards"
        if self.action_is_change_color():
            return repr(self.cards_to_put) + " Change color to:" + str(self.change_color)
        return repr(self.cards_to_put)

    def __eq__(self, other):
        return other.get_cards() == self.get_cards() and self.get_change_color() == other.get_change_color()

    def __hash__(self):
        return hash((tuple(self.cards_to_put), self.change_color))

    def __add__(self, other):
        return Action(self.cards_to_put + other.cards_to_put, no_op=False, change_color=other.change_color)