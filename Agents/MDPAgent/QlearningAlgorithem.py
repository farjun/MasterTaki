from AIex4Files.game import *
from AIex4Files.learningAgents import ReinforcementAgent
import numpy as np

import random
import AIex4Files.util as util

class QLearningAgent():
    """
      Q-Learning Agent
      Functions you should fill in:
        - getQValue
        - getAction
        - getValue
        - getPolicy
        - update
      Instance variables you have access to
        - self.epsilon (exploration prob)
        - self.alpha (learning rate)
        - self.discount (discount rate)
      Functions you should use
        - self.getLegalActions(state)
          which returns legal actions
          for a state
    """

    def __init__(self,actionFn = None, numTraining=100, epsilon=0.5, alpha=0.5, gamma=1,index=0):
        "You can initialize Q-values here..."
        self.QValues = util.Counter()
        self.index = index
        if actionFn == None:
            actionFn = lambda state: state.getLegalActions()
        self.actionFn = actionFn

        self.episodesSoFar = 0
        self.accumTrainRewards = 0.0
        self.accumTestRewards = 0.0

        self.numTraining = int(numTraining)
        self.epsilon = float(epsilon)
        self.alpha = float(alpha)
        self.discount = float(gamma)

    def getQValue(self, state, action):
        """
          Returns Q(state,action)
          Should return 0.0 if we never seen
          a state or (state,action) tuple
        """
        return self.QValues[state, action]

    def getValue(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if len(actions) == 0:
            return 0.
        qvalues = np.array([self.getQValue(state, action) for action in actions])
        return max(qvalues)

    def getPolicy(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        actions = self.getLegalActions(state)
        if len(actions) == 0:
            return None
        qvalues = np.array([self.getQValue(state, action) for action in actions])
        maxActions = np.array(actions)[np.argwhere(qvalues == np.max(qvalues)).flatten()]
        return np.random.choice(maxActions)

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
        legalActions = self.getLegalActions(state)
        if len(legalActions) == 0:
            return None
        action = random.choice(legalActions) if util.flipCoin(self.epsilon) else self.getPolicy(state)
        return action

    def update(self, state, action, nextState, reward):
        """
          The parent class calls this to observe a
          state = action => nextState and reward transition.
          You should do your Q-Value update here
          NOTE: You should never call this function,
          it will be called on your behalf
        """
        self.QValues[state, action] = self.getQValue(state, action) + \
                                      self.alpha * (reward + self.discount * self.getValue(nextState)
                                                    - self.getQValue(state, action))

        ###############################
        ### from Reinforcment Agent ###
        ###############################

    def observeTransition(self, state, action, nextState, deltaReward):
        """
            Called by environment to inform agent that a transition has
            been observed. This will result in a call to self.update
            on the same arguments

            NOTE: Do *not* override or call this function
        """
        self.episodeRewards += deltaReward
        self.update(state, action, nextState, deltaReward)

    def getLegalActions(self, state):
        """
          Get the actions available for a given
          state. This is what you should use to
          obtain legal actions for a state
        """
        return self.actionFn(state)

    def startEpisode(self):
        """
          Called by environment when new episode is starting
        """
        self.lastState = None
        self.lastAction = None
        self.episodeRewards = 0.0

    def stopEpisode(self):
        """
          Called by environment when episode is done
        """
        if self.episodesSoFar < self.numTraining:
            self.accumTrainRewards += self.episodeRewards
        else:
            self.accumTestRewards += self.episodeRewards
        self.episodesSoFar += 1
        if self.episodesSoFar >= self.numTraining:
            # Take off the training wheels
            self.epsilon = 0.0  # no exploration
            self.alpha = 0.0  # no learning

    def isInTraining(self):
        return self.episodesSoFar < self.numTraining

    def isInTesting(self):
        return not self.isInTraining()


    def setEpsilon(self, epsilon):
        self.epsilon = epsilon

    def setLearningRate(self, alpha):
        self.alpha = alpha

    def setDiscount(self, discount):
        self.discount = discount

    def doAction(self, state, action):
        """
            Called by inherited class when
            an action is taken in a state
        """
        self.lastState = state
        self.lastAction = action



