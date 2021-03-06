from TakiGame.DeckStuff.Card import Number, SpecialNoColor, SpecialWithColor, Color, Card
from random import shuffle

NUMBER_OF_COPIES_FOR_KING = 2
NUMBER_OF_COPIES_FOR_SUPER_TAKI = 2
NUMBER_OF_COPIES_FOR_CHANGE_COLOR = 4
NUM_OF_COPIES_FOR_COLOR_CARDS = 2


class Deck:
    def __init__(self, use_shuffle=True):
        self.cards_deck = list()
        self.init_deck()
        if use_shuffle:
            self.shuffle()

    def init_deck(self):
        self.cards_deck = list()
        for i in range(NUM_OF_COPIES_FOR_COLOR_CARDS):
            for color in Color:
                if color is not Color.NO_COLOR:
                    for number in Number:
                        self.cards_deck.append(Card(number, color))

                    for special_with_color_card in SpecialWithColor:
                        # if special_with_color_card == SpecialWithColor.TAKI:
                        #     continue
                        self.cards_deck.append(Card(special_with_color_card, color))

        for i in range(NUMBER_OF_COPIES_FOR_KING):
            self.cards_deck.append(Card(SpecialNoColor.KING, Color.NO_COLOR))
        for i in range(NUMBER_OF_COPIES_FOR_SUPER_TAKI):
            self.cards_deck.append(Card(SpecialNoColor.SUPER_TAKI, Color.NO_COLOR))
        for i in range(NUMBER_OF_COPIES_FOR_CHANGE_COLOR):
            self.cards_deck.append(Card(SpecialNoColor.CHANGE_COLOR, Color.NO_COLOR))

    def shuffle(self):
        shuffle(self.cards_deck)

    def set_deck(self, cards):
        shuffle(cards)
        self.cards_deck = cards

    def get_deck(self):
        return self.cards_deck

    def get_number_of_cards_left(self):
        return len(self.cards_deck)

    def deal(self, num_of_cards_to_deal=1):
        return [self.cards_deck.pop() for i in range(num_of_cards_to_deal)]

    def __iter__(self):
        return self.cards_deck.__iter__()


