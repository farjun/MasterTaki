import numpy as np
import copy
from Agents.TreeBasedAgents.TreeBasedAgent import TreeBasedAgent


NUM_OF_ITERATIONS = 5
MAX_SCORE = 1000
MIN_SCORE = 0

class ExpectimaxAgent(TreeBasedAgent):

    def __init__(self,game, evaluation_function, depth=2):
        super().__init__(game, evaluation_function, depth, "ExpectimaxAgent", self.recursive_expectimax)


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

