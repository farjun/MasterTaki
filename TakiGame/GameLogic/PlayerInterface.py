from TakiGame.GameLogic.Action import Action
class PlayerInterface:
    """
    just override get action with a class inheriting from this interface
    """
    def __init__(self, name):
        self.name = name
        self.cards = list()

    def get_action(self)->Action:
        pass

    def player_is_done(self):
        return len(self.cards) == 0

    def take_cards(self,cards_to_take):
        self.cards.extend(cards_to_take)

    def use_cards(self, cards_to_use):
        for card in cards_to_use:
            try:
                self.cards.index(card)
            except:
                print(card)
                raise CardNotInHandException


class CardNotInHandException(Exception):
    pass
