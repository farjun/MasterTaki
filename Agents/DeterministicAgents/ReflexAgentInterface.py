import numpy as np

from Agents.PlayerInterface import PlayerInterface


class HeuristicReflexAgent(PlayerInterface):

    def __init__(self, game, H):
        super().__init__("HeuristicReflexAgent", game)
        self.H = H

    def choose_action(self, randomly_choose_from_max=False):
        """
        chooses action using the heuristic function it got
        :param all_legal_actions: all possible legal actions
        :return: the max score given to each legal action
        """
        all_legal_actions = self.game.get_legal_actions(self.cards)
        all_legal_actions_scores = list()
        for legal_action in all_legal_actions:
            action_score = self.H(legal_action, self.game, self.cards)
            all_legal_actions_scores.append(action_score)

        max_score = max(all_legal_actions_scores)
        all_indexes_equal_to_max = [i for i, score in enumerate(all_legal_actions_scores) if score == max_score]

        if randomly_choose_from_max:
            random_index = np.random.choice(all_indexes_equal_to_max, 1)
            return all_legal_actions[random_index]
        else:
            not_random_index = np.random.choice(all_indexes_equal_to_max, 1)[0]
            return all_legal_actions[not_random_index]









