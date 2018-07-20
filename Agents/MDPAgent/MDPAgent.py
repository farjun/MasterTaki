from TakiGame.Players.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
import numpy as np


class MDPAgent(PlayerInterface):
    def __init__(self, game):
        super().__init__("POMDPAgent", game)
        self.is_fully_observable = True


    def choose_action(self):
        """
        :return: best action every
        """
        cur_state = self.game.get_cur_state(self.cards, full_state = self.is_fully_observable)
        




