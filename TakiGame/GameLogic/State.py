
class TwoPlayerState(object):
    def __init__(self, cur_players_cards, top_card, other_player_cards):
        self.cur_players_cards = cur_players_cards
        self.top_card = top_card
        self.other_player_cards = other_player_cards

    def get_cur_player_cards(self):
        return self.cur_players_cards

    def get_top_card(self):
        return self.top_card

    def get_other_player_info(self):
        return None

    def __hash__(self):
        return hash((tuple(self.cur_players_cards),self.top_card,tuple(self.other_player_cards)))


class FullStateTwoPlayer(TwoPlayerState):
    def __init__(self, cur_players_cards, top_card, other_player_cards):
        super().__init__(cur_players_cards, top_card, other_player_cards)

    def get_other_player_info(self):
        return self.other_player_cards

    def __eq__(self, other):
        return other.cur_players_cards == self.cur_players_cards and \
               other.top_card == self.top_card and \
               other.other_player_cards == self.other_player_cards


class PartialStateTwoPlayer(TwoPlayerState):
    def __init__(self, cur_players_cards, top_card, other_player_cards):
        super().__init__(cur_players_cards, top_card, other_player_cards)

    def get_other_player_info(self):
        return len(self.other_player_cards)

    def __eq__(self, other):
        return other.cur_players_cards == self.cur_players_cards and \
               other.top_card == self.top_card and \
               len(other.other_player_cards) == len(self.other_player_cards)

    def __hash__(self):
        return hash((tuple(self.cur_players_cards),self.top_card,tuple(self.other_player_cards)))