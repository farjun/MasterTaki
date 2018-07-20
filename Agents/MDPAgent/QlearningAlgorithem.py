from Agents.ex4files.game import *
from Agents.ex4files.learningAgents import ReinforcementAgent
import numpy as np

import random,math
import Agents.ex4files.util as util

class QLearningAgent(ReinforcementAgent):
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
  def __init__(self, **args):
    "You can initialize Q-values here..."
    ReinforcementAgent.__init__(self, **args)
    self.QValues = util.Counter()

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
                                  self.alpha*(reward + self.discount*self.getValue(nextState)
                                              -self.getQValue(state, action))
