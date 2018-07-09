from TakiGame.Players.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
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


    def choose_action(self,mode = 'sum',randomly_choose_from_max = False):
        """
        chooses action using the heuristic function it got
        :param all_legal_actions: all possible legal actions
        :param mode: 'sum' mode = using the sum score of each heuristic on an action
                    'avg' mode = using the avg score of each heuristic on an action
        :return: the max score given to each legal action
        """
        all_legal_actions = self.game.get_legal_actions(self.cards)
        all_legal_actions_scores = list()
        for legal_action in all_legal_actions:
            if self.parameter_learning: # todo I don't understand what it means so for now I have assign it as false
                action_score = self._get_action_score_by_mode([h(self,legal_action) for h in self.H], mode)
                all_legal_actions_scores.append(action_score)
            else:
                action_score = self._get_action_score_by_mode([h(self,legal_action) for h in self.H], mode)
                all_legal_actions_scores.append(action_score)

        max_score = max(all_legal_actions_scores)
        all_indexs_equal_to_max = [i for i, score in enumerate(all_legal_actions_scores) if score == max_score]

        if randomly_choose_from_max:
            random_index = np.random.choice(all_indexs_equal_to_max,1)
            return all_legal_actions[random_index]
        else:
            not_random_index = np.random.choice(all_indexs_equal_to_max, 1)[0]
            return all_legal_actions[not_random_index]

    def back_propogation(self,won):
        pass

    def color_heuristic(self, action):
        """
        A simple heuristic that quantify action based on the wanting to finish all the cards of the active color
        :param action: A set of cards
        :return: the heuristic cost
        """
        if action.action_is_draw():
            return 0
        first_card_color = action.get_cards()[0].color
        last_card_color = action.get_cards()[-1].color

        # If the active color is no-color then the agent wouldn't mind changing the color
        if self.game.active_color == Color.NO_COLOR:
            return len(action.get_cards())
        # If the action starts with super taki and ends with the active color
        if action.begin_with_super_taki() and self.game.active_color == last_card_color:
            return len(action.get_cards())
        # Count the number of cards that are in the same color as the active color
        counter = 0
        for card in self.cards:
            if card.color == self.game.active_color:
                counter += 1

        # return the number of cards that the action encapsulate if the color is the same as the active color
        if counter >= 1:
            if self.game.active_color == first_card_color:
                return len(action.get_cards())
            return 0
        else: # else the agent doesn't mind
            return len(action.get_cards())# todo maybe just 1








