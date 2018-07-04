from TakiGame.GameLogic.Action import Action


class PlayerInterface:
    """
    just override get action with a class inheriting from this interface
    """
    def __init__(self, name, game):
        self.name = name
        self.cards = list()
        self.game = game

    def choose_action(self,all_leagal_actions)->Action:
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


class CardNotInHandException(Exception):
    pass
