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


class ExpectimaxAgent(PlayerInterface):

    def __init__(self,game, evaluation_function, depth=2):
        super().__init__("ExpectimaxAgent", game)
        self.evaluation_function = evaluation_function
        self.depth = depth

    def recursive_expectimax(self, game, depth, agent):
        """
        Given a certain depth of the tree this function estimates the value of the each action of the agent.
        Where in the case of the our agent it will do so by maximize the result otherwise it will average the action
        score.
        :param game: A object that encapsulates the taki game
        :param depth: The expected depth of the tree
        :param agent: The agent
        :return: In the end it will return the best action for our agent and its score
        """
        # At the depth zero return the score
        if depth == 0:
            return self.evaluation_function[0](game.get_state()), None
        # If it is our turn
        game_state = game.get_state()
        cards = game.get_current_player_hand()

        legal_actions = game.get_legal_actions(cards)
        if agent == 0:

            # In case it's the end of the recursion branch
            if not len(legal_actions):
                return self.evaluation_function[0](game_state), None

            future_scores = self.operate_actions_in_a_single_depth(legal_actions, game, depth, agent, MAX_SCORE)

            # Return the max score and the action
            argmax_score = np.argmax(future_scores)
            return future_scores[argmax_score], legal_actions[argmax_score]
        # It's the computer turn
        if agent == 1:

            # In case it's the end of the recursion branch
            if not len(legal_actions):
                return self.evaluation_function[0](game_state), None
            # Return the mean the averaged score

            future_scores = self.operate_actions_in_a_single_depth(legal_actions, game, depth - 1, agent, MIN_SCORE)
            return np.mean(future_scores), None

    def operate_actions_in_a_single_depth(self, legal_actions, game, depth, agent, end_game_score):
        """
        Go through all of the legal actions i.e given a state perform all of the legal actions and continue
        the recursive function from the state s' <- s,a
        :param legal_actions: The actions that are legal given the agent hand and the top of the pile
        :param game: A object that encapsulates the taki game
        :param depth: The expected depth of the tree
        :param agent: The agent
        :param end_game_score: A score that signify the end of the game
        :return: The action taken by the agent
        """
        future_scores = []

        for action in legal_actions:
            # Play the agent turn
            current_game = copy.deepcopy(game)
            current_game.run_single_turn(action, True)
            # In case the action will lead to the end of the game then return a predetermined score and action
            if current_game.is_end_game():
                return [end_game_score]
            future_scores.append(self.recursive_expectimax(current_game,
                                                           depth, not agent)[0])

        return future_scores

    def recursive_expectimax_on_number_of_hands(self, game):
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

        for i in range(0, final_num_of_iterations):
            # Set current game
            current_game = copy.deepcopy(game)
            current_game.set_deck(deck)
            current_game.set_opp_hand(hand)

            # Apply Expectimax
            actions[self.recursive_expectimax(current_game, self.depth, 0)[1]] += 1

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
        return self.recursive_expectimax_on_number_of_hands(current_game)


class AlphaBetaPruningAgent(PlayerInterface):

    def __init__(self,game, evaluation_function, depth=2):
        super().__init__("AlphaBetaPruningAgent", game)
        self.evaluation_function = evaluation_function
        self.depth = depth




    def recursive_alphabeta_pruning(self, game, depth, agent, alpha, beta):
        """
        Given a certain depth of the tree this function estimates the value of the each action of the agent.
        Where in the case of the our agent it will do so by maximize the result otherwise it will average the action
        score.
        :param game: A object that encapsulates the taki game
        :param depth: The expected depth of the tree
        :param agent: The agent
        :return: In the end it will return the best action for our agent and its score
        """
        # At the depth zero return the score
        if depth == 0:
            return self.evaluation_function[0](game.get_state()), None
        # If it is our turn
        game_state = game.get_state()
        cards = game.get_current_player_hand()

        legal_actions = game.get_legal_actions(cards)
        if agent == 0:

            # In case it's the end of the recursion branch
            if len(legal_actions) == 1:
                return self.evaluation_function[0](game_state), legal_actions[0]

            max_score = MIN_SCORE
            max_action = None

            for action in legal_actions:
                # Play the agent turn
                current_game = copy.deepcopy(game)
                current_game.run_single_turn(action, True)
                # In case the action will lead to the end of the game then return a predetermined score and action
                if current_game.is_end_game():
                    return [MAX_SCORE]
                cur_score = self.recursive_alphabeta_pruning(current_game,
                                                             depth, not agent,alpha, beta)[0]
                if max_score < cur_score:
                    max_score = cur_score
                    max_action = action
                alpha = max(alpha, cur_score)

                if beta <= alpha:
                    break

            # Return the max score and the action
            return max_score, max_action

        # It's the computer turn
        if agent == 1:

            # In case it's the end of the recursion branch
            if len(legal_actions) == 1:
                return self.evaluation_function[0](game_state), legal_actions[0]
            # Return the mean the averaged score

        min_score = MAX_SCORE
        min_action = None

        for action in legal_actions:
            # Play the agent turn
            current_game = copy.deepcopy(game)
            current_game.run_single_turn(action, True)
            # In case the action will lead to the end of the game then return a predetermined score and action
            if current_game.is_end_game():
                return [MIN_SCORE]
            cur_score = self.recursive_alphabeta_pruning(current_game,
                                                         depth - 1, not agent, alpha, beta)[0]
            if min_score > cur_score:
                min_score = cur_score
                min_action = action
            beta = min(beta, cur_score)

            if beta <= alpha:
                break

        # Return the max score and the action
        return min_score, min_action

    # def operate_actions_in_a_single_depth(self, legal_actions, game, depth, agent, end_game_score, max_score, min_score,
    #                                       alpha, beta):
    #     """
    #     Go through all of the legal actions i.e given a state perform all of the legal actions and continue
    #     the recursive function from the state s' <- s,a
    #     :param legal_actions: The actions that are legal given the agent hand and the top of the pile
    #     :param game: A object that encapsulates the taki game
    #     :param depth: The expected depth of the tree
    #     :param agent: The agent
    #     :param end_game_score: A score that signify the end of the game
    #     :return: The action taken by the agent
    #     """
    #     future_scores = []
    #
    #
    #     for action in legal_actions:
    #         # Play the agent turn
    #         current_game = copy.deepcopy(game)
    #         current_game.run_single_turn(action, True)
    #         # In case the action will lead to the end of the game then return a predetermined score and action
    #         if current_game.is_end_game():
    #             return [end_game_score]
    #         cur_score = self.recursive_alphabeta_pruning(current_game,
    #                                                      depth, not agent)[0]
    #         if not agent:
    #             if max_score < cur_score:
    #                 max_score = cur_score
    #             alpha = max(alpha, cur_score)
    #
    #         if agent and min_score > cur_score:
    #             min_score = cur_score
    #             beta = min(beta, cur_score)
    #
    #         if beta <= alpha:
    #             return
    #         future_scores.append(cur_score)
    #     return future_scores

    def recursive_alphabeta_on_number_of_hands(self, game):
        """
        Operate the recursive_alphabeta function a number of times on different opponent hands
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

        for i in range(0, final_num_of_iterations):
            # Set current game
            current_game = copy.deepcopy(game)
            current_game.set_deck(deck)
            current_game.set_opp_hand(hand)

            # Apply Expectimax
            actions[self.recursive_alphabeta_pruning(current_game, self.depth, 0, MIN_SCORE, MAX_SCORE)[1]] += 1

            # Get the next hand
            hand, deck = pr.random_hand(opponent_num_of_cards, game)
            while tuple(hand) in set_of_hands:
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
        return self.recursive_alphabeta_on_number_of_hands(current_game)