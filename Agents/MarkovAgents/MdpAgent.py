import random

from Agents.Rewards import total_cards_dropped_reward
from TakiGame.Players.PlayerInterface import PlayerInterface
from util import Counter, flipCoin
import numpy as np
REWARD_FUNCTION = total_cards_dropped_reward

class MDPAgent(PlayerInterface):
    def __init__(self, game, counter_weights):
        super().__init__("MDP", game)

        self.is_fully_observable = True
        self.Q_values = counter_weights

        # constants
        self.alpha = float(0.9)
        self.epsilon = float(0.05)
        self.gamma = float(0.8)
        self.discount = float(0.5)

    def choose_action(self):
        """
        :return: best action we can do
        """
        cur_state = self.game.get_state()
        all_leagal_actions = self.game.logic.get_leagal_actions_from_state(cur_state)
        if flipCoin(self.epsilon):
            return random.choice(all_leagal_actions)
        else:
            return self.getPolicy(cur_state)


    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        "*** YOUR CODE HERE ***"
        if (state,action) not in self.Q_values.keys():
            return 0
        return self.Q_values[(state,action)]

    def getValue(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        "*** YOUR CODE HERE ***"
        legal_actions = self.getLegalActions(state)
        return max([self.getQValue(state, action) for action in legal_actions],default=0)

    def getPolicy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        legal_actions = self.game.logic.get_leagal_actions_from_state(state)
        if len(legal_actions) == 1:
            return legal_actions[0]  # change to take card
        q_values = np.asarray([self.getQValue(state, action) for action in legal_actions])
        max_index = np.where(q_values == np.max(q_values))  # find all indexes of max element
        return legal_actions[random.choice(max_index[0])]  # get random from max

    def update(self, state, action, nextState):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here

          NOTE: You should never call this function,
          it will be called on your behalf
        """
        "*** YOUR CODE HERE ***"
        if (state, action) not in self.Q_values.keys():
            self.Q_values[(state, action)] = 0

        reward = REWARD_FUNCTION(state, action, nextState)
        next_action = self.getPolicy(nextState)
        self.Q_values[(state, action)] += self.alpha*(reward+self.discount*self.getQValue(nextState,next_action) - self.getQValue(state, action))

    def getLegalActions(self, state):
        cur_cards = state.get_cur_player_cards()
        return self.game.logic.get_legal_actions(cur_cards)


