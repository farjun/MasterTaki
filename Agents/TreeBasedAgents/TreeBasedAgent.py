import numpy as np
import copy
import scipy.special as scipy
import Probabilities.Probabilities as pr
from util import Counter
from TakiGame.Players.PlayerInterface import PlayerInterface
import sys

NUM_OF_ITERATIONS = 5
MAX_SCORE = 1000
MIN_SCORE = 0

class TreeBasedAgent(PlayerInterface):

    def __init__(self,game, evaluation_function, depth=2, agent_type="TreeBasedAgent", recursive_function=None):
        super().__init__(agent_type, game)
        self.evaluation_function = evaluation_function
        self.depth = depth
        self.recursive_function = recursive_function

    def tree_recursion_on_number_of_hands(self, game):
        """
        Operate the recursive_expectimax function a number of times on different opponent hands
        :param game: A object that encapsulates the taki game
        :return: The action that was chosen most of the times as the best course of action
        """
        # A set that will contain a set of cards (i.e hands) so they wouldn't be duplicated
        set_of_hands = set()
        actions = Counter()
        opponent_num_of_cards = game.get_other_players_number_of_cards()[0]

        # Get the opponent hand
        hand, deck = pr.random_hand(opponent_num_of_cards, game)
        set_of_hands.add(tuple(hand))
        deck_size = len(deck)

        # Achieve the number of iterations possible
        final_num_of_iterations = min(NUM_OF_ITERATIONS, scipy.binom(deck_size + opponent_num_of_cards,
                                                                     opponent_num_of_cards))
        print("number of actions: ",len(game.get_legal_actions(game.get_current_player_hand())))

        for i in range(0, final_num_of_iterations):
            # Set current game
            current_game = copy.deepcopy(game)
            current_game.set_deck(deck)
            current_game.set_opp_hand(hand)

            actions[self.recursive_function(current_game, self.depth, 0)[1]] += 1
            # Get the next hand
            hand, deck = pr.random_hand(opponent_num_of_cards, game)
            while(tuple(hand) in set_of_hands):
                hand, deck = pr.random_hand(opponent_num_of_cards, game)

            set_of_hands.add(tuple(hand))

        # We chose to return the action which occurred the most
        return actions.argMax()

    def choose_action(self):
        current_game = copy.deepcopy(self.game)
        legal_actions = current_game.get_legal_actions(current_game.get_current_player_hand())
        if len(legal_actions) == 1:
            # only possible action is draw card, so draw card
            return legal_actions[0]
        return self.tree_recursion_on_number_of_hands(current_game)
