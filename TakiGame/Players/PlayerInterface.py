from TakiGame.GameLogic.Action import Action
from sortedcontainers import SortedList


class PlayerInterface:
    """
    just override get action with a class inheriting from this interface
    """
    def __init__(self, name, game):
        self.name = name
        self.cards = SortedList()
        self.game = game

    def get_name(self):
        return self.name

    def choose_action(self)->Action:
        pass

    def update(self, state, action, nextState):
        return None

    def player_is_done(self):
        return len(self.cards) == 0

    def take_cards(self, cards_to_take):
        for card in cards_to_take:
            self.cards.add(card)

    def use_cards(self, cards_to_use):
        for card in cards_to_use:
            self.cards.remove(card)

    def get_number_of_cards(self):
        return len(self.cards)

    def get_cards(self):
        return self.cards

    def set_cards(self, cards):
        self.cards = SortedList()
        self.take_cards(cards)


class CardNotInHandException(Exception):
    pass
