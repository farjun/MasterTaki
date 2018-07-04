from itertools import permutations

import sys

from TakiGame.Agents.PlayerInterface import PlayerInterface
from TakiGame.DeckStuff.Card import Color
from TakiGame.DeckStuff.TakiDeck import Deck
from TakiGame.GameLogic.Action import Action
from TakiGame.Agents.ManualAgent import ManualAgent


class NotEnoughPlayersException(Exception):
    pass


NUM_OF_CARDS_TO_DEAL = 8


class GameManager:
    def __init__(self, playersTypes):
        self.deck = Deck()
        self.pile = list()
        if len(playersTypes) < 2:
            raise NotEnoughPlayersException
        self.players = self.__init_players(playersTypes)
        self.cur_player_index = -1
        self.number_of_cards_to_draw = 1
        self.progress_direction = 1
        self.first_turn = True
        self.active_color = Color.NO_COLOR

    def __init_players(self, playersTypes):
        players = []
        for player in playersTypes.values():
            if player[1] == "M":
                players.append(ManualAgent(player[1], self))
        return players

    def __move_to_next_players_turn(self):
        self.cur_player_index = (self.cur_player_index + 1 * self.progress_direction) % len(self.players)

    def __deal_players(self):
        for player in self.players:
            hand = self.deck.deal(NUM_OF_CARDS_TO_DEAL)
            player.take_cards(hand)

    def __update_deck(self):
        card_on_top = self.pile.pop()
        self.deck.set_deck(self.pile.copy())
        self.pile = [card_on_top]

    def __execute_draw(self):
        if self.number_of_cards_to_draw > self.deck.get_number_of_cards_left():
            self.__update_deck()
        cards_to_take = self.deck.deal(self.number_of_cards_to_draw)
        self.players[self.cur_player_index].take_cards(cards_to_take)
        self.number_of_cards_to_draw = 1

    def __execute_action(self, action):
        self.players[self.cur_player_index].use_cards(action.get_cards())
        if action.action_is_draw():
            self.__execute_draw()
        if action.action_is_stop():
            self.__move_to_next_players_turn()
        if action.action_is_change_direction():
            self.progress_direction = -1 * self.progress_direction
        if action.action_is_plus_2():
            self.number_of_cards_to_draw = 2 if self.number_of_cards_to_draw == 1 else self.number_of_cards_to_draw + 2
        if action.action_is_plus():
            self.cur_player_index = self.cur_player_index - self.progress_direction  # player will get another turn
        if action.action_is_king():
            self.number_of_cards_to_draw = 1
            self.cur_player_index = self.cur_player_index - self.progress_direction  # player will get another turn
        self.pile.extend(action.get_cards())
        if action.action_is_change_color():
            self.active_color = action.action_get_change_color()
        else:
            self.active_color = self.pile[-1].get_color()
        self.first_turn = False  # important for starting the game with plus 2

    # def __check_if_action_is_legal(self, action):
    #     if action.action_is_draw():
    #         # todo - check the deck isnt over
    #         return True
    #     temp_pile = list()
    #     for card in action:
    #         if card.is_taki_card:
    #             pass # enter taki mode
    #         # else handle it
    #         card_on_top_of_pile = self.pile[-1]

    def __search_for_king(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_king()]

    def __search_for_plus_2(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_plus_2()]

    def __subsets(self, same_color_cards):
        for cardinality in range(1, (len(same_color_cards) + 1)):
            yield from permutations(same_color_cards, cardinality)

    def __end_taki_with_no_color_actions(self, current_subset, no_color_cards):
        actions = []
        change_color_indices = [i for i in range(len(no_color_cards)) if no_color_cards[i].is_change_color()]
        for index in change_color_indices:
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
        current_color_cards = [card for card in player_cards if card.get_color() is color and not card.is_taki_card(color)]
        taki_cards = [card for card in player_cards if card.is_taki_card(color)]
        no_color_cards = [card for card in player_cards if
                          card.get_color() is Color.NO_COLOR and not card.is_taki_card(Color.NO_COLOR)]
        subsets = []
        for i in range(len(taki_cards)):
            current_subset = [Action([taki_cards[i]] + list(s)) for s in self.__subsets(current_color_cards)]  # add the taki card
            subsets.extend(current_subset)
            # taki can end with no color card, add those options to every existing option
            subsets.extend(self.__end_taki_with_no_color_actions(current_subset, no_color_cards))
        return subsets

    def __search_color_cards(self, player_cards, color):
        if color is Color.NO_COLOR:  # todo maybe change for more oop-y function
            possible_actions = self.__add_no_color_actions(player_cards)
            for other_color in Color:
                if other_color is not Color.NO_COLOR:  # prevent infinite loop, add all possible options from other colors
                    possible_actions.extend(self.__search_color_cards(player_cards, other_color))
                    possible_actions.extend(self.__generate_taki_card_moves(player_cards, other_color))
        else:
            possible_actions = [Action([card]) for card in player_cards if card.get_color() is color]
            possible_actions.extend(self.__generate_taki_card_moves(player_cards, color))
        return possible_actions

    def __search_same_value_cards(self, player_cards, value):
        possible_actions = [Action([card]) for card in player_cards if card.get_value() is value]
        return possible_actions

    def __active_plus_2(self):
        return self.number_of_cards_to_draw > 1 or self.first_turn

    def __add_no_color_actions(self, player_cards):
        no_color_actions = []
        no_color_cards = [card for card in player_cards if card.get_color() is Color.NO_COLOR]
        for card in no_color_cards:
            if card.is_change_color():
                no_color_actions.extend([Action([card], no_op=False, change_color=other_color)
                                         for other_color in Color if other_color is not Color.NO_COLOR])
            else:
                no_color_actions.extend(Action([card]))
        return no_color_actions

    def get_legal_actions(self, player_cards):
        legal_actions = [Action([], no_op=True)]
        card_on_top_of_pile = self.pile[-1]
        if card_on_top_of_pile.is_plus_2() and self.__active_plus_2():
            legal_actions.extend(self.__search_for_plus_2(player_cards))
            legal_actions.extend(self.__search_for_king(player_cards))
            return legal_actions
        legal_actions.extend(self.__search_color_cards(player_cards, self.active_color))
        legal_actions.extend(self.__search_same_value_cards(player_cards, card_on_top_of_pile.get_value()))
        if self.active_color is not Color.NO_COLOR:  # prevent duplications - no color cards can be placed on any card
            legal_actions.extend(self.__add_no_color_actions(player_cards))
        return legal_actions

    def get_other_players_number_of_cards(self):
        number_of_cards = [self.players[(self.cur_player_index + i * self.progress_direction) % len(self.players)].get_number_of_cards()
                           for i in range(1, len(self.players))]
        return number_of_cards

    def __init_state(self):
        self.pile.extend(self.deck.deal())
        self.active_color = self.pile[-1].get_color()
        self.number_of_cards_to_draw = 2 if self.pile[-1].is_plus_2() else 1  # start the game with plus 2

    def run_game(self):
        self.__deal_players()
        self.__init_state()
        self.__move_to_next_players_turn()
        cur_player = self.players[self.cur_player_index]

        while True:
            print("Player %d turn:" % self.cur_player_index)
            print("******\nLeading Card: %s\n******" % self.pile[-1])
            cur_action = cur_player.choose_action()
            self.__execute_action(cur_action)
            if cur_player.player_is_done() and not cur_action.action_is_plus():
                break  # todo update the winner or something like that
            self.__move_to_next_players_turn()
            cur_player = self.players[self.cur_player_index]
        print("Player %d is the winner" % (self.cur_player_index + 1))


if __name__ == '__main__':
    # players = readCommand( sys.argv[1:] ) # Get game components based on input
    players = {"Player1": ["Ido", "M"], "Player2": ["Shachar", "M"]}
    game = GameManager(players)
    game.run_game()
