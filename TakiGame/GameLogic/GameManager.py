from itertools import permutations

import sys

from TakiGame.Players.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
from TakiGame.DeckStuff.TakiDeck import Deck
from TakiGame.GameLogic.Action import Action
from TakiGame.Players.ManualAgent import ManualAgent
from Agents.DeterministicAgents.ReflexAgentInterface import HeuristicReflexAgent
from Agents.DeterministicAgents import Heuristics
from TakiGame.GameLogic.FullStateTwoPlayer import PartialStateTwoPlayer, FullStateTwoPlayer


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

    def __init_players(self, playersTypes):
        players = {}
        for id, player_details in enumerate(playersTypes.values()):
            if player_details[1] == "M":
                players[id] = [ManualAgent(player_details[PLAYER_NAME], self), "Manual", 0]
            if player_details[1] == "H":
                players[id] = [HeuristicReflexAgent(self, [Heuristics.color_heuristic], False),"Heuristic",0]
        return players

    def __move_to_next_players_turn(self):
        """
        Change current player index to next player, according to game direction.
        """
        self.cur_player_index = (self.cur_player_index + 1 * self.progress_direction) % len(self.players)
        return self.players[self.cur_player_index][PLAYER]

    def __deal_players(self):
        """
        Deal the initial hand of any player.
        :return:
        """
        for player in self.players.values():
            hand = self.deck.deal(NUM_OF_CARDS_TO_DEAL)
            player[PLAYER].take_cards(hand)

    def __update_deck(self):
        """
        Move all but top card from the pile to the empty deck.
        """
        card_on_top = self.pile.pop()
        self.deck.set_deck(self.pile.copy())
        self.pile = [card_on_top]

    def __execute_draw(self):
        """
        Draw current number of cards to draw from the deck and give them to the current player.
        """
        if self.number_of_cards_to_draw > self.deck.get_number_of_cards_left():
            cards_to_take = self.deck.deal(self.deck.get_number_of_cards_left())
            self.players[self.cur_player_index][PLAYER].take_cards(cards_to_take)
            self.number_of_cards_to_draw -= self.deck.get_number_of_cards_left()
            self.__update_deck()

        cards_to_take = self.deck.deal(self.number_of_cards_to_draw)
        self.players[self.cur_player_index][PLAYER].take_cards(cards_to_take)
        self.number_of_cards_to_draw = 1

    def __execute_action(self, action):
        """
        Execute and change game state according to the given action.
        :param action: action to execute.
        """
        self.players[self.cur_player_index][PLAYER].use_cards(action.get_cards())  # remove cards from player's hand
        if action.action_is_stop():
            self.__move_to_next_players_turn()  # skip next player turn
        if action.action_is_change_direction() and len(self.players) > 2:  # change direction has no affect on 2 players game
            self.progress_direction = -1 * self.progress_direction
        if action.action_is_plus_2():
            # update number of cards to draw
            self.number_of_cards_to_draw = 2 if self.number_of_cards_to_draw == 1 else self.number_of_cards_to_draw + 2
        if action.action_is_plus():
            self.another_turn = True  # player will get another turn
        if action.action_is_king():
            # withdraw active plus 2 and get another turn
            self.number_of_cards_to_draw = 1
            self.another_turn = True  # player will get another turn
        if action.action_is_draw():
            self.__execute_draw()
        self.pile.extend(action.get_cards())  # add action's card to the pile
        if action.action_is_change_color():
            self.active_color = action.action_get_change_color()
        else:
            # change active color to top card color unless it was change color card and other players draw
            self.active_color = self.pile[-1].get_color() if not self.pile[-1].is_change_color() else self.active_color
        self.first_turn = False  # important for starting the game with plus 2

    def __search_for_king(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_king()]

    def __search_for_plus_2(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_plus_2()]

    def __subsets(self, same_color_cards):
        """
        Gets every subset of the given color cards, for open taki move purposes.
        :param same_color_cards:
        """
        for cardinality in range(1, (len(same_color_cards) + 1)):
            yield from permutations(same_color_cards, cardinality)

    def __end_taki_with_no_color_actions(self, current_subset, no_color_cards):
        """
        Add no color cards to the end of every possible open taki move.
        :param current_subset: list of every possible open taki move
        :param no_color_cards: list of special cards with no color from current player's hand
        :return: list of actions of open taki moves that ends with no color card.
        """
        actions = []
        change_color_indices = [i for i in range(len(no_color_cards)) if no_color_cards[i].is_change_color()]
        for index in change_color_indices:
            # add every possible color for change color action
            actions.extend([Action(s.get_cards() + [no_color_cards[index]], no_op=False, change_color=color)
                        for color in Color if color is not Color.NO_COLOR
                        for s in current_subset])
        if len(change_color_indices) < len(no_color_cards):
            # add other no color cards
            actions.extend([Action(s.get_cards() + [special_card])
                        for special_card in no_color_cards if not special_card.is_change_color()
                        for s in current_subset])
        return actions

    def __generate_taki_card_moves(self, player_cards, color):
        """
        Generates every possible open taki move from the given cards and color.
        :param player_cards: current player's hand.
        :param color: color for open taki move.
        :return: list of every possible open taki move from the given cards and color.
        """
        current_color_cards = [card for card in player_cards if card.get_color() is color and not card.is_taki_card(color)]
        taki_cards = [card for card in player_cards if card.is_taki_card(color)]
        no_color_cards = [card for card in player_cards if
                          card.get_color() is Color.NO_COLOR and not card.is_taki_card(Color.NO_COLOR)]
        subsets = []
        for i in range(len(taki_cards)):
            current_subset = [Action([taki_cards[i]] + list(s)) for s in self.__subsets(current_color_cards)]  # add the taki card
            subsets.extend(current_subset)
            # open taki in any color can end with no color card, add those options to every existing option
            subsets.extend(self.__end_taki_with_no_color_actions(current_subset, no_color_cards))
        return subsets

    def __search_color_cards(self, player_cards, color):
        """
        Generates every possible move from the given cards and color.
        :param player_cards: current player's hand.
        :param color: color for taki move.
        :return: list of all possible actions from the given cards and oolor.
        """
        if color is Color.NO_COLOR:
            possible_actions = []
            for other_color in Color:
                if other_color is not Color.NO_COLOR:  # prevent infinite loop, add all possible options from other colors
                    possible_actions.extend(self.__search_color_cards(player_cards, other_color))
        else:
            possible_actions = [Action([card]) for card in player_cards if card.get_color() is color]
            possible_actions.extend(self.__generate_taki_card_moves(player_cards, color))
        return possible_actions

    def __search_same_value_cards(self, player_cards, active_card):
        """
        Generates every possible move from the given player's cards and the active card value.
        :param player_cards: current player's hand.
        :param active_card: top of the pile card.
        :return: list of all possible actions from the given cards and the active card value.
        """
        possible_actions = []
        if active_card.is_taki_card(active_card.get_color()):
            # add all possible open taki moves
            for other_color in Color:
                if other_color is not active_card.get_color():
                    possible_actions.extend(self.__generate_taki_card_moves(player_cards, other_color))
        else:
            possible_actions.extend([Action([card]) for card in player_cards if card.get_value() is active_card.get_value()])
        return possible_actions

    def __active_plus_2(self, active_card):
        """
        Check if there is an active plus 2 card at this current game state.
        :param active_card: top of the pile card.
        :return: true if there is an active plus 2, false otherwise.
        """
        return active_card.is_plus_2() and (self.number_of_cards_to_draw > 1 or self.first_turn)

    def __add_no_color_actions(self, player_cards):
        """
        Generates all possible no color moves from given player's cards.
        :param player_cards: current player's cards.
        :return: list of all possible no color actions from the given cards.
        """
        no_color_actions = []
        no_color_cards = [card for card in player_cards if card.get_color() is Color.NO_COLOR]
        for card in no_color_cards:
            if card.is_change_color():
                no_color_actions.extend([Action([card], no_op=False, change_color=other_color)
                                         for other_color in Color if other_color is not Color.NO_COLOR])
            else:
                no_color_actions.extend([Action([card])])
        return no_color_actions

    def get_legal_actions(self, player_cards):
        """

        :param player_cards:
        :return:
        """
        legal_actions = [Action([], no_op=True)]  # draw card action
        card_on_top_of_pile = self.pile[-1]
        if self.__active_plus_2(card_on_top_of_pile):
            # only king or plus 2 cards can answer to active plus 2
            legal_actions.extend(self.__search_for_plus_2(player_cards))
            legal_actions.extend(self.__search_for_king(player_cards))
            return legal_actions
        legal_actions.extend(self.__search_color_cards(player_cards, self.active_color))
        legal_actions.extend(self.__search_same_value_cards(player_cards, card_on_top_of_pile))
        legal_actions.extend(self.__add_no_color_actions(player_cards))
        return legal_actions

    def get_other_players_number_of_cards(self):
        """
        Returns list of other players number of cards in hand, sorting from next player to last player.
        :return: list of other players number of cards in hand, sorting from next player to last player.
        """
        number_of_cards = [self.players[(self.cur_player_index + i * self.progress_direction) % len(self.players)].get_number_of_cards()
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
        self.cur_player_index = 0
        self.__deal_players()
        self.pile.extend(self.deck.deal())
        self.active_color = self.pile[-1].get_color()
        self.number_of_cards_to_draw = 2 if self.pile[-1].is_plus_2() else 1  # start the game with plus 2

    def __update_winner(self):
        """
        Print end game message and update scoring table.
        """
        self.cur_player_index = max(self.cur_player_index, 0)  # final action was king action
        if self.print_mode:
            print("\n******\nPlayer %d is the winner\n******\n" % (self.cur_player_index + 1))
        self.players[self.cur_player_index][PLAYER_SCORE] += 1

    def __run_single_game(self):
        """
        Runs single taki game and update scoring table according to game's result.
        """
        self.__init_state()
        cur_player = self.players[self.cur_player_index][PLAYER]
        while True:
            if self.print_mode:
                print("Player %d turn:" % (self.cur_player_index+1))
                print("******\nLeading Card: %s\nLeading Color: %s\n******" % (self.pile[-1].get_value(), self.active_color))
            cur_action = cur_player.choose_action()
            self.__execute_action(cur_action)
            if cur_player.player_is_done() and not cur_action.action_is_plus():
                self.__update_winner()
                return
            if not self.another_turn:
                cur_player = self.__move_to_next_players_turn()
            else:
                self.another_turn = False

    def run_game(self):
        for i in range(self.number_of_games):
            self.__run_single_game()

    def print_scoring_table(self):
        for player in self.players.values():
            print("Player Name: %s\nPlayer Type: %s\nPlayer Score: %s" % (player[PLAYER].get_name(),
                                                                          player[PLAYER_TYPE],
                                                                          player[PLAYER_SCORE]))

    def get_current_player_hand(self):
        return self.players[self.cur_player_index][PLAYER].get_cards()

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
    players = {"Player1": ["Ido", "H"], "Player2": ["Shachar", "H"]}
    number_of_games = 100
    game = GameManager(players, number_of_games, print_mode=False)
    game.run_game()
    game.print_scoring_table()
