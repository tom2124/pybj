from random import choice

# ------- #
# CLASSES #
# ------- #


class Card:
    SUITS = ("Spades", "Clubs", "Hearts", "Diamonds")
    suit = None

    def __init__(self, suit):
        self.suit = suit


class PictureCard(Card):
    KINDS = ("King", "Queen", "Jack", "Ace")
    kind = None

    def __init__(self, suit, kind):
        super(suit)
        self.kind = kind


class NumberCard(Card):
    value = None

    def __init__(self, suit, value):
        super(suit)
        self.value = value


class Deck:
    cards = []
    kind = None

    class Kind:
        CSM = "Continuous Shuffling Machine"
        SINGLE = "Single"
        MDS = "Multi-Deck Shoe"

    def single_deck():
        cards = []
        for suit in Card.SUITS:
            for number in range(2, 10):
                cards.append(NumberCard(suit, number))
            for kind in PictureCard.KINDS:
                cards.append(PictureCard(suit, kind))
        return cards

    def __init__(self, kind):
        self.kind = kind
        self.cards = self.single_deck()
        # 1 if we're using a single deck, 6 if we're using a MDS,
        # this field is ignored if we're using a CSM
        self.num_decks = 1 if kind == Deck.Kind.SINGLE else 6

    def draw(self):
        if self.kind == self.Kind.CSM:
            return choice(self.cards)
        elif self.kind == self.kind.SINGLE or self.kind == self.kind.MDS:
            card = choice(self.cards)
            self.cards.remove(card)

            if len(self.cards) == 0:
                for _ in range(1, self.num_decks):
                    self.cards.append(self.single_deck())

            return card
