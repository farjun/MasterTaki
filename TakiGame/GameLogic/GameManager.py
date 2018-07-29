from Agents import Heuristics
from Agents.DeterministicAgents import StateHeuristics
from Agents.DeterministicAgents.ReflexAgentInterface import HeuristicReflexAgent
from Agents.MarkovAgents.MdpAgent import MDPAgent
from Agents.MarkovAgents.PomdpAgent import POMDPAgent
from Agents.TreeBasedAgents.AlphaBetaPruningAgent import AlphaBetaPruningAgent
from Agents.TreeBasedAgents.ExpectimaxAgent import ExpectimaxAgent
from TakiGame.DeckStuff.TakiDeck import Deck
from TakiGame.GameLogic.LogicExecutor import LogicExecutor
from TakiGame.GameLogic.State import PartialStateTwoPlayer, FullStateTwoPlayer
from TakiGame.Players.ManualAgent import ManualAgent
from util import Counter

class NotEnoughPlayersException(Exception):
    pass


NUM_OF_CARDS_TO_DEAL = 8
PLAYER = 0
PLAYER_TYPE = 1
PLAYER_SCORE = 2
PLAYER_NAME = 0


class GameManager:
    def __init__(self, playersTypes, games, print_mode=False, counter_weights_list=[Counter(), Counter()]):
        if len(playersTypes) < 2:
            raise NotEnoughPlayersException
        self.players = self.__init_players(playersTypes, counter_weights_list)
        self.number_of_games = games
        self.print_mode = print_mode
        self.deck = None
        self.logic = LogicExecutor(self)

    def __init_players(self, playersTypes, counter_weights_list):
        players = {}
        for id, player_details in enumerate(playersTypes):
            if player_details[1] == "M":
                players[id] = [ManualAgent(player_details[PLAYER_NAME], self), "Manual", 0]
            if player_details[1] == "H":
                players[id] = [HeuristicReflexAgent(self, [Heuristics.color_heuristic], False), "Heuristic", 0]
            if player_details[1] == "A":
                players[id] = [AlphaBetaPruningAgent(self, [StateHeuristics.weight_heuristic], 2), "AlphaBetaPruning", 0]
            if player_details[1] == "E":
                players[id] = [ExpectimaxAgent(self, [StateHeuristics.weight_heuristic], 2), "Expectimax", 0]
            if player_details[1] == 'MDP':
                players[id] = [MDPAgent(self, counter_weights_list[0]),"MDPAgent",0]
            if player_details[1] == 'POMDP':
                players[id] = [POMDPAgent(self, counter_weights_list[1]),"POMDPAgent",0]
        return players

    def __deal_players(self):
        """
        Deal the initial hand of any player.
        :return:
        """
        for player in self.players.values():
            player[PLAYER].set_cards(list())
            hand = self.deck.deal(NUM_OF_CARDS_TO_DEAL)
            player[PLAYER].take_cards(hand)

    def get_legal_actions(self, player_cards):
        """

        :param player_cards:
        :return:
        """
        return self.logic.get_legal_actions(player_cards)

    def get_other_players_number_of_cards(self):
        """
        Returns list of other players number of cards in hand, sorting from next player to last player.
        :return: list of other players number of cards in hand, sorting from next player to last player.
        """
        number_of_cards = [self.players[(self.cur_player_index + i * self.progress_direction) % len(self.players)][PLAYER].get_number_of_cards()
                           for i in range(1, len(self.players))]
        return number_of_cards

    def __init_new_game(self):
        """
        Inits all relevant parameters for new taki game.
        """
        self.deck = Deck()
        self.pile = list()
        self.progress_direction = 1
        self.first_turn = True
        self.another_turn = False
        self.end_game = False
        self.cur_player_index = 0
        self.__deal_players()
        self.pile.extend(self.deck.deal())
        self.active_color = self.pile[-1].get_color()
        self.players_states = {}
        self.number_of_cards_to_draw = 2 if self.pile[-1].is_plus_2() else 1  # start the game with plus 2

    def save_current_state(self, cur_action):
        self.players_states[self.cur_player_index] = (self.get_state(), cur_action)

    def update_agent(self):
        if self.cur_player_index in self.players_states:
            player_last_state, player_last_action = self.players_states[self.cur_player_index]
        else:
            # else this is his first turn, get None as action and current state as state
            player_last_state = self.get_state()
            player_last_action = None
        self.get_current_player().update(player_last_state, player_last_action, self.get_state())

    def run_single_turn(self, cur_action, simulate=False):
        self.save_current_state(cur_action)
        self.logic.run_single_turn(cur_action, simulate)
        self.update_agent()

    def is_end_game(self):
        return self.end_game

    def run_single_game(self, simulate=False):
        """
        Runs single taki game and update scoring table according to game's result.
        """
        self.__init_new_game()
        while True:
            if self.print_mode and not simulate:
                print("Player %d turn:" % (self.cur_player_index+1))
                print("******\nLeading Card: %s\nLeading Color: %s\n******" % (self._top_card().get_value(), self.active_color))
            cur_action = self.get_current_player().choose_action()
            self.run_single_turn(cur_action, simulate)
            if self.end_game:
                return

    def run_game(self):
        for i in range(self.number_of_games):
            self.run_single_game()

    def print_scoring_table(self):
        for player in self.players.values():
            print("Player Name: %s\nPlayer Type: %s\nPlayer Score: %s" % (player[PLAYER].get_name(),
                                                                          player[PLAYER_TYPE],
                                                                           player[PLAYER_SCORE]))

    def _top_card(self):
        return self.pile[-1]

    def get_current_player(self):
        return self.players[self.cur_player_index][PLAYER]

    def get_current_player_hand(self):
        return self.players[self.cur_player_index][PLAYER].get_cards()

    def set_opp_hand(self, cards):
        self.players[(self.cur_player_index + 1 * self.progress_direction) % len(self.players)][PLAYER].set_cards(cards)

    def get_number_of_players(self):
        return len(self.players)

    def get_deck(self):
        return self.deck

    def set_deck(self, cards):
        self.deck.set_deck(cards)

    def get_pile(self):
        return self.pile

    def get_top_card(self):
        return self.pile[-1]

    def get_state(self):
        current_player_hand = self.get_current_player_hand().copy()
        opp_player_hand = self.players[(self.cur_player_index + 1 * self.progress_direction) % len(self.players)][PLAYER].get_cards().copy()
        if self.players[self.cur_player_index][PLAYER_TYPE] != "MDP":
            return PartialStateTwoPlayer(current_player_hand, self.get_top_card(), opp_player_hand)
        else:
            return FullStateTwoPlayer(current_player_hand, self.get_top_card(), opp_player_hand)


if __name__ == '__main__':
    # players, number_of_games = readCommand( sys.argv[1:] ) # Get game components based on input
    players = [["Ido", "H"], ["Shachar", "MDP"]]
    number_of_games = 150
    number_of_training = 1000
    game = GameManager(players, number_of_games, print_mode=True)
    for i in range(number_of_games):
        game.run_single_game(True)

    game.run_game()
    game.print_scoring_table()

    print(len(game.players[1][PLAYER].Q_values))

