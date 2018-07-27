
import copy
from Agents.TreeBasedAgents.TreeBasedAgent import TreeBasedAgent
import sys


class AlphaBetaPruningAgent(TreeBasedAgent):

    def __init__(self, game, evaluation_function, depth=2):
        super().__init__(game, evaluation_function, depth, "AlphaBetaPruningAgent", self.recursive_alphabeta_pruning)

    def recursive_alphabeta_pruning(self, game, depth, agent, alpha=-sys.maxsize, beta=sys.maxsize):
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

            max_score = -sys.maxsize
            max_action = None

            for action in legal_actions:
                # Play the agent turn
                current_game = copy.deepcopy(game)
                current_game.run_single_turn(action, True)
                # In case the action will lead to the end of the game then return a predetermined score and action
                if current_game.is_end_game():
                    return sys.maxsize, action
                cur_score = self.recursive_alphabeta_pruning(current_game,
                                                             depth, not agent,alpha, beta)[0]
                if max_score <= cur_score:
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

            min_score = sys.maxsize
            min_action = None

            for action in legal_actions:
                # Play the agent turn
                current_game = copy.deepcopy(game)
                current_game.run_single_turn(action, True)
                # In case the action will lead to the end of the game then return a predetermined score and action
                if current_game.is_end_game():
                    return -sys.maxsize, action
                cur_score = self.recursive_alphabeta_pruning(current_game,
                                                             depth - 1, not agent, alpha, beta)[0]
                if min_score >= cur_score:
                    min_score = cur_score
                    min_action = action
                beta = min(beta, cur_score)

                if beta <= alpha:
                    break

            # Return the max score and the action
            return min_score, min_action
