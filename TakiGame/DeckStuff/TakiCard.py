
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
    PLUS_3 = 4

class TakiCard:

  def __init__(self,number_or_special,color:Color):
      self.color = color
      self.number_or_special = number_or_special


