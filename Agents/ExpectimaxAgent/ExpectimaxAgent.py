import numpy as np
import copy
import scipy.special as scipy
import Probabilities.Probabilities as pr
from util import Counter

NUM_OF_ITERATIONS = 10
MAX_SCORE = 1000
MIN_SCORE = 0


class ExpectimaxAgent:

    def __init__(self, evaluation_function, depth=2):
        self.evaluation_function = evaluation_function
        self.depth = depth

    def recursive_expectimax(self, game, depth, agent):
        # At the depth zero return the score
        if depth == 0:
            return self.evaluation_function(game.get_state()), None
        # If it is our turn
        # todo deal with the end of the game
        game_state = game.get_state()
        cards = game.get_current_player_hand()

        legal_actions = game.get_legal_actions(cards)
        if agent == 0:

            # In case it's the end of the recursion branch
            if not len(legal_actions):
                return self.evaluation_function(game_state), None

            future_scores = self.operate_actions_in_a_single_depth(legal_actions, game, depth, not agent, MAX_SCORE)

            # Return the max score and the action
            argmax_score = np.argmax(future_scores)
            return future_scores[argmax_score], legal_actions[argmax_score]
        # It's the computer turn
        if agent == 1:

            # In case it's the end of the recursion branch
            if not len(legal_actions):
                return self.evaluation_function(game_state), None
            # Return the mean the averaged score

            future_scores = self.operate_actions_in_a_single_depth(legal_actions, game, depth - 1, not agent, MIN_SCORE)
            return np.mean(future_scores), None



    def operate_actions_in_a_single_depth(self, legal_actions, game,depth, agent,end_game_score):
        future_scores = []

        for action in legal_actions:
            current_game = copy.deepcopy(game)
            current_game.run_single_turn(action)
            if current_game.end_game():
                return end_game_score, action
            future_scores.append(self.recursive_expectimax(current_game.get_state(),
                                                           depth, not agent)[0])

        return future_scores

    def recursive_expectimax_on_number_of_hands(self, game):

        set_of_hands = set()
        actions = Counter()
        opponent_num_of_card = game.get_other_players_number_of_cards()[0]


        hand, deck = pr.random_hand(opponent_num_of_card, game)
        set_of_hands.add(hand)
        deck_size = len(deck)

        final_num_of_iterations = min(NUM_OF_ITERATIONS, scipy.binom(deck_size + opponent_num_of_card, opponent_num_of_card))

        for i in range(0, final_num_of_iterations):
            # Set current game
            current_game = copy.deepcopy(game)
            current_game.set_deck(deck)
            current_game.set_opp_hand(hand)

            # Apply Expecimax
            actions[self.recursive_expectimax(current_game, self.depth, 0)[1]] += 1

            hand, deck = pr.random_hand(opponent_num_of_card, game)
            while(hand in set_of_hands):
                hand, deck = pr.random_hand(opponent_num_of_card, game)

            set_of_hands.add(hand)

        # We chose to return the action which occurred the most
        return actions.argMax()






