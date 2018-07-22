from TakiGame.GameLogic.Action import Action

class PlayerInterface:
    """
    just override get action with a class inheriting from this interface
    """
    def __init__(self, name, game):
        self.name = name
        self.cards = list()
        self.game = game

    def get_name(self):
        return self.name

    def choose_action(self)->Action:
        pass

    def player_is_done(self):
        return len(self.cards) == 0

    def take_cards(self, cards_to_take):
        self.cards.extend(cards_to_take)

    def use_cards(self, cards_to_use):
        for card in cards_to_use:
            self.cards.remove(card)

    def get_number_of_cards(self):
        return len(self.cards)

    def get_cards(self):
        return self.cards

    def set_cards(self, cards):
        self.cards = cards


class CardNotInHandException(Exception):
    pass
