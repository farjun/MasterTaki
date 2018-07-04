from TakiGame.GameLogic.Action import Action
from TakiGame.Players.PlayerInterface import PlayerInterface


class ManualAgent(PlayerInterface):

    def choose_action(self)->Action:
        possible_actions = self.game.get_legal_actions(self.cards)
        print("Current hand:")
        print(self.cards)
        print("Possible Actions:")
        for i in range(len(possible_actions)):
            print("Action index: %d\nAction: %s" % (i, possible_actions[i]))
        chosen_index = int(input("Insert chosen action index:"))
        return possible_actions[chosen_index]