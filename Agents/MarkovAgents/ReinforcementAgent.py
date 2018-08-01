import random
from Agents.Rewards import total_cards_dropped_reward, TERMINAL_STATE_SCORE
from TakiGame.Players.PlayerInterface import PlayerInterface
from util import flipCoin
import numpy as np

REWARD_FUNCTION = total_cards_dropped_reward


class ReinforcementAgent(PlayerInterface):

    def __init__(self, game, POMDP_flag, counter_weights):
        if POMDP_flag:
            super().__init__("POMDPAgent", game)
        else:
            super().__init__("MDPAgent", game)

        self.is_fully_observable = POMDP_flag
        self.Q_values = counter_weights
        self.repeat_state_action_counter = 0

        # constants
        self.alpha = float(0.9)
        self.epsilon = float(0.05)
        self.discount = float(0.1)

    def choose_action(self):
        """
        :return: best action we can do
        """
        cur_state = self.game.get_state()
        all_legal_actions = self.game.logic.get_legal_actions_from_state(cur_state)
        if flipCoin(self.epsilon):
            return random.choice(all_legal_actions)
        else:
            return self.getPolicy(cur_state)

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        return self.Q_values[(state, action)]

    def getValue(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legal_actions = self.getLegalActions(state)
        return max([self.getQValue(state, action) for action in legal_actions], default=0)

    def getPolicy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        legal_actions = self.game.logic.get_legal_actions_from_state(state)
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
        reward = REWARD_FUNCTION(state, action, nextState)
        if self.Q_values[(state, action)] != 0:
            self.repeat_state_action_counter += 1
        if abs(reward) == TERMINAL_STATE_SCORE:
            # game is over, there is no meaning for next state so don't take it to account
            self.Q_values[(state, action)] += self.alpha * reward
        else:
            next_action = self.getPolicy(nextState)
            self.Q_values[(state, action)] += self.alpha * (reward + self.discount *
                                                            self.getQValue(nextState, next_action) -
                                                            self.getQValue(state, action))

    def getLegalActions(self, state):
        cur_cards = state.get_cur_player_cards()
        return self.game.logic.get_legal_actions(cur_cards)

    def init_repeat_counter(self):
        self.repeat_state_action_counter = 0

    def get_repeat_counter(self):
        return self.repeat_state_action_counter


