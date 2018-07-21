import random

from TakiGame.Players.PlayerInterface import PlayerInterface
from AIex4Files.util import Counter,flipCoin
from TakiGame.GameLogic.GameManager import GameManager

import Agents.MDPAgent.QlearningAlgorithem as QlearningAlgorithem
from TakiGame.DeckStuff.Card import Color
import numpy as np


class MDPAgent(PlayerInterface):
    def __init__(self, game : GameManager):
        super().__init__("MDP", game)

        self.is_fully_observable = True
        self.Q_values = Counter()

        # constants
        self.alpha = float(1.0)
        self.epsilon = float(0.05)
        self.gamma = float(0.8)
        self.discount = float(0.5)

    def choose_action(self):
        """
        :return: best action we can do
        """
        cur_state = self.game.get_state()


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
        legal_actions = self.getLegalActions(state)
        if len(legal_actions)  ==0:
            return None
        q_valuse =np.asarray([self.getQValue(state, action) for action in legal_actions])
        max_index= np.where(q_valuse== np.max(q_valuse)) #find all indexes of max element
        return legal_actions[random.choice(max_index[0])] #get random from max
        # util.raiseNotDefined()



    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        # Pick Action
        legal_actions = self.getLegalActions(state)
        "*** YOUR CODE HERE ***"
        if len(legal_actions) == 0:
            return None
        if flipCoin(self.epsilon):
            return random.choice(legal_actions)
        return self.getPolicy(state) #best chose


    def update(self, state, action, nextState, reward):
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
        next_action= self.getPolicy(nextState)
        self.Q_values[(state, action)] += self.alpha*(reward+self.discount*self.getQValue(nextState,next_action)- self.getQValue(state, action))

        # util.raiseNotDefined()

    def getLegalActions(self, state):
        cur_cards = state.get_cur_player_cards()
        return self.game.logic.get_legal_actions(cur_cards)


