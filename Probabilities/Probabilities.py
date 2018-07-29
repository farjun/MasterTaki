
from TakiGame.DeckStuff.TakiDeck import Deck


def random_hand(number_of_cards, game):
    """
    Return a random set of cards that are sampled uniformly from the current deck.
    The size of the set will be as the number of cards in the opponent hand
    :param number_of_cards: The number of cards in the opponent hand
    :param game: A object of the game
    :return: A random set of cards
    """

    deck = get_current_deck(game)
    adversary_hand = []
    for i in range(0, number_of_cards):
        adversary_hand.append(deck.pop())

    return adversary_hand, deck


def get_current_deck(game):
    """
    Will initiate a deck and subtract the cards that are in the pile or our hand
    :param game: A object of the game
    :return: The current deck with the opponent hand
    """

    deck = Deck().cards_deck
    # Remove cards that are in the pile
    flag = True
    for num, card in enumerate(game.pile):
        if card not in deck and flag:
            print("Card not in deck: %s\nCard index: %d\nDeck: %s\nPile: %s\n" % (card, num, deck, game.pile))
            flag = False
        else:
            deck.remove(card)

    # Remove cards that are in the current player hand
    for card in game.get_current_player_hand():
        if card not in deck:
            print("Card not in deck: %s\nDeck: %s\n" % (card, deck))
        else:
            deck.remove(card)

    return deck
