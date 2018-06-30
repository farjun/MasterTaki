from enum import Enum


class Color(Enum):
    NO_COLOR = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4


class Number(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


class SpecialWithColor(Enum):
    PLUS_2 = 1
    PLUS = 2
    STOP = 3
    CHANGE_DIRECTION = 4
    TAKI = 5
    CRAZY_CARD = 6


class SpecialNoColor(Enum):
    CHANGE_COLOR = 1
    SUPER_TAKI = 2
    KING = 3


SPECIAL_CARDS_WHICH_HAVE_NO_MORE_CARDS_TO_PUT_ON = {SpecialNoColor.CHANGE_COLOR, SpecialWithColor.CRAZY_CARD,
                                                    SpecialNoColor.KING}


class Card:
    def __init__(self, number_or_special, color: Color):
        self.color = color
        self.number_or_special = number_or_special

    def can_have_more_cards_on_top(self):
        return self.number_or_special not in SPECIAL_CARDS_WHICH_HAVE_NO_MORE_CARDS_TO_PUT_ON

    def can_be_placed_on(self, other):
        if self.number_or_special in Number or self.number_or_special in SpecialWithColor:
            return self.color == other.color

        if self.number_or_special in SpecialNoColor:
            return True

    def is_taki_card(self):
        return self.number_or_special is SpecialNoColor.SUPER_TAKI or self.number_or_special is SpecialWithColor.TAKI


    def __eq__(self, other):
        return self.color == other.color and self.number_or_special == other.number_or_special
