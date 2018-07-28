from itertools import permutations, combinations

from TakiGame.DeckStuff.Card import Color
from TakiGame.GameLogic.Action import Action
from TakiGame.GameLogic.State import FullStateTwoPlayer

PLAYER_SCORE = 2


class LogicExecutor:
    def __init__(self, game):
        self.game = game

    def __update_deck(self):
        """
        Move all but top card from the pile to the empty deck.
        """
        card_on_top = self.game.get_pile().pop()
        self.game.set_deck(self.game.get_pile().copy())
        self.game.pile = [card_on_top]

    def __execute_draw(self):
        """
        Draw current number of cards to draw from the deck and give them to the current player.
        """
        if self.game.number_of_cards_to_draw > self.game.get_deck().get_number_of_cards_left():
            cards_to_take = self.game.get_deck().deal(self.game.get_deck().get_number_of_cards_left())
            self.game.get_current_player().take_cards(cards_to_take)
            self.game.number_of_cards_to_draw -= self.game.get_deck().get_number_of_cards_left()
            self.__update_deck()

        cards_to_take = self.game.get_deck().deal(self.game.number_of_cards_to_draw)
        self.game.get_current_player().take_cards(cards_to_take)
        self.game.number_of_cards_to_draw = 1

    def __move_to_next_players_turn(self):
        """
        Change current player index to next player, according to game direction.
        """
        self.game.cur_player_index = (self.game.cur_player_index + 1 * self.game.progress_direction) % self.game.get_number_of_players()

    def __execute_action(self, action):
        """
        Execute and change game state according to the given action.
        :param action: action to execute.
        """
        self.game.get_current_player().use_cards(action.get_cards())  # remove cards from player's hand
        if action.action_is_king():
            # withdraw active plus 2
            self.game.number_of_cards_to_draw = 1
        if self.game.get_number_of_players() > 2:
            if action.action_is_stop():
                # in two players game current player gets another turn, it's already include in current action
                self.__move_to_next_players_turn()  # skip next player turn
            if action.action_is_change_direction():  # change direction has no affect on 2 players game
                self.game.progress_direction = -1 * self.game.progress_direction
        if action.action_is_plus_2():
            # update number of cards to draw
            self.game.number_of_cards_to_draw = 2 if self.game.number_of_cards_to_draw == 1 else self.game.number_of_cards_to_draw + 2
        self.game.get_pile().extend(action.get_cards())  # add action's card to the pile
        if action.action_is_draw() or self.game.get_top_card().is_plus():
            # top card is plus only if current player doesn't have more cards with this color, so draw him a card
            self.__execute_draw()
        if action.action_is_stop() and self.game.get_number_of_players() == 2 and \
            not self.game.get_current_player().player_is_done():
            # if action top card is stop and player does not finished his hand he have to draw a card
            self.__execute_draw()
        if action.action_is_change_color():
            self.game.active_color = action.get_change_color()
        else:
            # change active color to top card color unless it was change color card and other players draw
            self.game.active_color = self.game.get_pile()[-1].get_color() \
                if not self.game.get_pile()[-1].is_change_color() else self.game.active_color
        self.game.first_turn = False  # important for starting the game with plus 2

    def __search_for_king(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_king()]

    def __search_for_plus_2(self, player_cards):
        return [Action([card]) for card in player_cards if card.is_plus_2()]

    def __subsets_comb(self, same_color_cards):
        """
        Gets every combination of the given color cards, for open taki move purposes.
        :param same_color_cards:
        """
        for cardinality in range(1, (len(same_color_cards) + 1)):
            yield from combinations(same_color_cards, cardinality)


    def __end_taki_with_no_color_actions(self, taki_card, taki_combinations, no_color_cards):
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
            actions.extend([Action([taki_card] + s + [no_color_cards[index]], no_op=False, change_color=color)
                        for color in Color if color is not Color.NO_COLOR
                        for s in taki_combinations])
        if len(change_color_indices) < len(no_color_cards):
            # add other no color cards
            actions.extend([Action([taki_card] + s + [special_card])
                        for special_card in no_color_cards if not special_card.is_change_color()
                        for s in taki_combinations])
        return actions

    def __generate_taki_card_moves(self, player_cards, color):
        """
        Generates every possible open taki move from the given cards and color.
        :param player_cards: current player's hand.
        :param color: color for open taki move.
        :return: list of every possible open taki move from the given cards and color.
        """
        if color is Color.NO_COLOR:
            current_color_cards = [card for card in player_cards if card.get_color() is self.game.active_color and not card.is_taki_card(color)]
        else:
            current_color_cards = [card for card in player_cards if card.get_color() is color and not card.is_taki_card(color)]
        taki_cards = [card for card in player_cards if card.is_taki_card(color)]
        no_color_cards = [card for card in player_cards if
                          card.get_color() is Color.NO_COLOR and not card.is_taki_card(Color.NO_COLOR)]
        subsets = []
        for i in range(len(taki_cards)):
            relevent_taki_sets = [sorted(list(s)) for s in self.__subsets_comb(current_color_cards)]  # get all sets
            # change only the last card in each taki set and sort the rest to avoid redundancy
            taki_combinations = [s[:i] + s[i+1:] + [s[i]] for s in relevent_taki_sets for i in range(len(s))]
            current_subset = [Action([taki_cards[i]] + s) for s in taki_combinations]  # add the taki card
            subsets.extend(current_subset)
            # open taki in any color can end with no color card, add those options to every existing option
            subsets.extend(self.__end_taki_with_no_color_actions(taki_cards[i], relevent_taki_sets, no_color_cards))
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
        return active_card.is_plus_2() and (self.game.number_of_cards_to_draw > 1 or self.game.first_turn)

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

    def __add_another_turn_actions(self, player_cards, legal_actions):
        another_turn_actions = []
        for action in legal_actions:
            if action.action_is_plus() or action.action_is_king() or \
                    (action.action_is_stop() and self.game.get_number_of_players() == 2):
                player_cards_left = player_cards.copy()
                for card in action.get_cards():
                    player_cards_left.remove(card)
                another_turn_actions.extend([action + another_action for another_action in
                                             self.get_legal_actions(player_cards_left, action.get_top_card(), action.get_active_color(), False)])
        return another_turn_actions

    def get_leagal_actions_from_state(self,state:FullStateTwoPlayer):
        return self.get_legal_actions(state.cur_players_cards)

    def get_legal_actions(self, player_cards, card_on_top_of_pile = None, active_color = None, include_draw = True):
        """

        :param player_cards:
        :return:
        """
        if not card_on_top_of_pile:
            card_on_top_of_pile = self.game.get_pile()[-1]
        if not active_color:
            active_color = self.game.active_color
        if include_draw:
            legal_actions = [Action([], no_op=True)]  # draw card action
        else:
            legal_actions = []
        if self.__active_plus_2(card_on_top_of_pile):
            # only king or plus 2 cards can answer to active plus 2
            legal_actions.extend(self.__search_for_plus_2(player_cards))
            legal_actions.extend(self.__search_for_king(player_cards))
            return sorted(list(set(legal_actions)), key=lambda x: len(x.get_cards()))
        legal_actions.extend(self.__search_color_cards(player_cards, active_color))
        legal_actions.extend(self.__search_same_value_cards(player_cards, card_on_top_of_pile))
        legal_actions.extend(self.__add_no_color_actions(player_cards))
        # add another turn options for plus or king actions and for stop action with 2 players game
        legal_actions.extend(self.__add_another_turn_actions(player_cards, legal_actions))
        return sorted(list(set(legal_actions)), key=lambda x: len(x.get_cards()))

    def __update_winner(self, simoulate=False):
        """
        Print end game message and update scoring table.
        """
        self.game.cur_player_index = max(self.game.cur_player_index, 0)  # final action was king action
        if not simoulate:
            print("\n******\nPlayer %d is the winner\n******\n" % (self.game.cur_player_index + 1))
            self.game.players[self.game.cur_player_index][PLAYER_SCORE] += 1
        self.game.end_game = True

    def run_single_turn(self, cur_action, simoulate=False):
        if not simoulate and self.game.print_mode:
            print(cur_action)
        self.__execute_action(cur_action)
        if self.game.get_current_player().player_is_done() and not self.game.get_top_card().is_plus():
            self.__update_winner(simoulate)
        if not self.game.end_game:
            self.__move_to_next_players_turn()

