from enum import Enum


class Color(Enum):
    NO_COLOR = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4

    def __lt__(self, other):
        return self.value < other.value


class Number(Enum):
    ONE = 1
    # TWO = 2 - apparently two and plus two is the same card
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9

    def __lt__(self, other):
        return self.value < other.value


class SpecialWithColor(Enum):
    PLUS_2 = 1
    PLUS = 2
    STOP = 3
    CHANGE_DIRECTION = 4
    TAKI = 5

    def __lt__(self, other):
        return self.value < other.value


class SpecialNoColor(Enum):
    CHANGE_COLOR = 1
    SUPER_TAKI = 2
    KING = 3

    def __lt__(self, other):
        return self.value < other.value


# SPECIAL_CARDS_WHICH_HAVE_NO_MORE_CARDS_TO_PUT_ON = {SpecialNoColor.CHANGE_COLOR, SpecialWithColor.CRAZY_CARD,
#                                                     SpecialNoColor.KING}  # not true for game with more than 2 players

SPECIAL_CARDS_WHICH_HAVE_MORE_CARDS_TO_PUT_ON = {SpecialNoColor.SUPER_TAKI, SpecialWithColor.TAKI, SpecialWithColor.PLUS}


class Card:
    def __init__(self, number_or_special, color: Color):
        self.color = color
        self.number_or_special = number_or_special

    def is_taki_card(self, color):
        return self.number_or_special is SpecialNoColor.SUPER_TAKI or \
               (self.number_or_special is SpecialWithColor.TAKI and self.color is color)

    def is_plus_2(self):
        return self.number_or_special is SpecialWithColor.PLUS_2

    def is_king(self):
        return self.number_or_special is SpecialNoColor.KING

    def is_change_direction(self):
        return self.number_or_special is SpecialWithColor.CHANGE_DIRECTION

    def is_change_color(self):
        return self.number_or_special is SpecialNoColor.CHANGE_COLOR

    def is_stop(self):
        return self.number_or_special is SpecialWithColor.STOP

    def is_plus(self):
        return self.number_or_special is SpecialWithColor.PLUS

    def is_super_taki(self):
        return self.number_or_special is SpecialNoColor.SUPER_TAKI

    def get_color(self):
        return self.color

    def get_value(self):
        return self.number_or_special

    def __eq__(self, other):
        return self.color == other.color and self.number_or_special == other.number_or_special

    def __lt__(self, other):
        if self.color < other.color:
            return True
        if self.color == other.color:
            if isinstance(self.number_or_special, type(other.number_or_special)):
                return self.number_or_special < other.number_or_special
            if isinstance(self.number_or_special, Number):
                return True
            if isinstance(other.number_or_special, Number):
                return False
            return isinstance(self.number_or_special, SpecialWithColor)
        return False

    def __hash__(self):
        return hash((self.color, self.number_or_special))

    def __repr__(self):
        return "<Card: %s\n color: %s>" % (self.number_or_special, self.color)

