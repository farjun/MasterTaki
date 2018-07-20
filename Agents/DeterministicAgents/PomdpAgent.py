from TakiGame.Players.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
import numpy as np

class POMDPAgent(PlayerInterface):

    def __init__(self, game):
        super().__init__("POMDPAgent", game)



    def choose_action(self):
        """
        :return: best action every
        """
        all_legal_actions = self.game.get_legal_actions(self.cards)


