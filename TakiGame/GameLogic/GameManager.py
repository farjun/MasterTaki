from itertools import permutations

import sys

from TakiGame.Players.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
from TakiGame.DeckStuff.TakiDeck import Deck
from TakiGame.GameLogic.Action import Action

from TakiGame.Players.ManualAgent import ManualAgent
from Agents.DeterministicAgents.ReflexAgentInterface import HeuristicReflexAgent

from Agents.DeterministicAgents import Heuristics, StateHeuristics
from TakiGame.GameLogic.State import PartialStateTwoPlayer, FullStateTwoPlayer
from TakiGame.GameLogic.LogicExecutor import LogicExecutor
from Agents.ExpectimaxAgent.ExpectimaxAgent import ExpectimaxAgent,AlphaBetaPruningAgent


class NotEnoughPlayersException(Exception):
    pass


NUM_OF_CARDS_TO_DEAL = 8
PLAYER = 0
PLAYER_TYPE = 1
PLAYER_SCORE = 2
PLAYER_NAME = 0


class GameManager:
    def __init__(self, playersTypes, games, print_mode=False):
        if len(playersTypes) < 2:
            raise NotEnoughPlayersException
        self.players = self.__init_players(playersTypes)
        self.number_of_games = games
        self.print_mode = print_mode
        self.deck = None
        self.logic = LogicExecutor(self)

    def __init_players(self, playersTypes):
        players = {}
        for id, player_details in enumerate(playersTypes):
            if player_details[1] == "M":
                players[id] = [ManualAgent(player_details[PLAYER_NAME], self), "Manual", 0]
            if player_details[1] == "H":
                players[id] = [HeuristicReflexAgent(self, [Heuristics.color_heuristic], False), "Heuristic", 0]
            if player_details[1] == "E":
                players[id] = [AlphaBetaPruningAgent(self, [StateHeuristics.color_and_remove_heuristic], 2), "AlphaBetaPruning", 0]
            if player_details[1] == "A":
                players[id] = [ExpectimaxAgent(self, [StateHeuristics.color_and_remove_heuristic], 2), "Expectimax", 0]
            if player_details[1] == 'MDP':
                players[id] = []
        return players

    def __deal_players(self):
        """
        Deal the initial hand of any player.
        :return:
        """
        for player in self.players.values():
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

    def __init_state(self):
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
        self.number_of_cards_to_draw = 2 if self.pile[-1].is_plus_2() else 1  # start the game with plus 2

    def run_single_turn(self, cur_action, simulate = False):
        self.logic.run_single_turn(cur_action, simulate)

    def is_end_game(self):
        return self.end_game

    def __run_single_game(self):
        """
        Runs single taki game and update scoring table according to game's result.
        """
        self.__init_state()
        while True:
            if self.print_mode:
                print("Player %d turn:" % (self.cur_player_index+1))
                print("******\nLeading Card: %s\nLeading Color: %s\n******" % (self.pile[-1].get_value(), self.active_color))
            cur_action = self.players[self.cur_player_index][PLAYER].choose_action()
            self.run_single_turn(cur_action)
            if self.end_game:
                return

    def run_game(self):
        for i in range(self.number_of_games):
            self.__run_single_game()

    def print_scoring_table(self):
        for player in self.players.values():
            print("Player Name: %s\nPlayer Type: %s\nPlayer Score: %s" % (player[PLAYER].get_name(),
                                                                          player[PLAYER_TYPE],
                                                                          player[PLAYER_SCORE]))

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
        current_player_hand = self.get_current_player_hand()
        opp_player_hand = self.players[(self.cur_player_index + 1 * self.progress_direction) % len(self.players)][PLAYER].get_cards()
        if self.players[self.cur_player_index][PLAYER_TYPE] != "MDP":
            return PartialStateTwoPlayer(current_player_hand, self.get_top_card(), opp_player_hand)
        else:
            return FullStateTwoPlayer(current_player_hand, self.get_top_card(), opp_player_hand)


if __name__ == '__main__':
    # players, number_of_games = readCommand( sys.argv[1:] ) # Get game components based on input
    players = [["Ido", "H"], ["Shachar", "A"]]
    number_of_games = 2
    game = GameManager(players, number_of_games, print_mode=True)
    game.run_game()
    game.print_scoring_table()
