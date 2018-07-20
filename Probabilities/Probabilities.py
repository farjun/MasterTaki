
from TakiGame.GameLogic import GameManager
from TakiGame.DeckStuff.TakiDeck import Deck


def random_hand(number_of_cards, game):
    """
    Return a random set of cards that are sampled uniformly from the current deck.
    The size of the set will be as the number of cards in the opponent hand
    :param number_of_cards: The number of cards in the opponent hand
    :param game: A object of the game
    :return: A random set of cards
    """
    deck = Deck().cards_deck
    # Remove cards that are in the pile
    for card in game.pile:
        deck.remove(card)

    # Remove cards that are in the current player hand
    for card in game.get_current_player_hand():
        deck.remove(card)

    adversary_hand = []
    for i in range(0, number_of_cards):
        adversary_hand.append(deck.pop())

    return adversary_hand

