from TakiGame.Players.PlayerInterface import PlayerInterface
import numpy as np

class HeuristicReflexAgent(PlayerInterface):

    def __init__(self, game,H,parameter_learning = False):
        super().__init__("HeuristicReflexAgent", game)
        self.H = H
        self.parameter_learning = parameter_learning
        if parameter_learning:
            self.weights = np.ones([len(H)])

    def _get_action_score_by_mode(self, score_array, mode):
        if mode == 'sum':
            return sum(score_array)
        elif mode =='avg':
            return sum(score_array) / float(len(score_array))


    def choose_action(self,all_leagal_actions,mode = 'sum',randomly_choose_from_max = False):
        """
        chooses action using the hruristic function it got
        :param all_leagal_actions: all possible leagal actions
        :param mode: 'sum' mode = using the sum score of each heuristic on an action
                    'avg' mode = using the avg score of each heuristic on an action
        :return: the max score given to each leagal action
        """
        all_leagal_actions_scores = list()
        for leagal_action in all_leagal_actions:
            if self.parameter_learning:
                action_score = self._get_action_score_by_mode([h(leagal_action) for h in self.H], mode)
                all_leagal_actions_scores.append(action_score)

        max_score = max(all_leagal_actions_scores)
        all_indexs_equal_to_max = [i for i, score in enumerate(all_leagal_actions_scores) if score == max_score]

        if randomly_choose_from_max:
            random_index = np.random.choice(all_indexs_equal_to_max,1)
            return all_leagal_actions[random_index]
        else:
            not_random_index = np.random.choice(all_indexs_equal_to_max, 1)
            return all_leagal_actions[not_random_index]

    def back_propogation(self,won):
        pass









