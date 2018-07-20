

class State(object):
    def __init__(self, cur_players_cards, top_card, other_player_cards):
        self.cur_players_cards = cur_players_cards
        self.top_card = top_card
        self.other_player_cards = other_player_cards

    def get_cur_player_cards(self):
        return self.cur_players_cards

    def get_top_card(self):
        return self.top_card

    def get_other_player_info(self):
        return self.other_player_cards


class PartialState(State):
    def __init__(self, cur_players_cards, top_card, other_player_cards):
        super().__init__(cur_players_cards, top_card, other_player_cards)

    def get_other_player_info(self):
        return len(self.other_player_cards)
