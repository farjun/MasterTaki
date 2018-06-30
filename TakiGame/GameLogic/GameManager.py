from TakiGame.DeckStuff.TakiDeck import Card, Deck
from TakiGame.GameLogic.PlayerInterface import PlayerInterface
class NotEnoghtPlayersException(Exception):
    pass

NUM_OF_CARDS_TO_DEAL = 8

class GameManager:
    def __init__(self, players: list(PlayerInterface)):
        self.deck = Deck()
        self.pile = list()
        if len(players)<2:
            raise NotEnoghtPlayersException

        self.players = players
        self.cur_player_index = -1

    def move_to_next_players_turn(self):
        if self.cur_player_index == len(self.players)-1:
            self.cur_player_index = 0
        else:
            self.cur_player_index += 1

    def deal_players(self):
        for player in self.players:
            hand = self.deck.deal(NUM_OF_CARDS_TO_DEAL)
            player.take_cards(hand)

    def check_if_action_is_leagal(self,action):
        if action.action_is_draw():
            # todo - check the deck isnt over
            return True
        temp_pile = list()
        for card in action:
            if not self.pile: # if pile is empty
                temp_pile.append(card)
                continue
            if card.is_taki_card:
                pass #enter taki mode
            # else handle it
            card_on_top_of_pile = self.pile[-1]


    def run_game(self):
        self.deal_players()
        self.move_to_next_players_turn()
        cur_player = self.players[self.cur_player_index]

        while not cur_player.player_is_done():
            cur_action = cur_player.get_action()




            self.move_to_next_players_turn()
            cur_player = self.players[self.cur_player_index]

