from Agents.PlayerInterface import PlayerInterface
from TakiGame.GameLogic.Action import Action


class ManualAgent(PlayerInterface):

    def choose_action(self)->Action:
        possible_actions = self.game.get_legal_actions(self.cards)
        print("Current hand:")
        print(self.cards)
        print("Possible Actions:")
        for i in range(len(possible_actions)):
            print("Action index: %d\nAction: %s" % (i, possible_actions[i]))
        chosen_index = int(input("Insert chosen action index:"))
        while chosen_index < 0 or chosen_index >= len(possible_actions):
            print("Wrong action index, index should be between 0 to %d" % (len(possible_actions)-1))
            chosen_index = int(input("Insert chosen action index:"))
        return possible_actions[chosen_index]