from random import choice

# ------- #
# CLASSES #
# ------- #


class Card(object):
    class Suit(object):
        SPADES = "Spades"
        CLUBS = "Clubs"
        HEARTS = "Hearts"
        DIAMONDS = "Diamonds"

    suit = None

    @staticmethod
    def all_suits():
        return (Card.Suit.SPADES, Card.Suit.CLUBS, Card.Suit.HEARTS, Card.Suit.DIAMONDS)

    def __init__(self, suit):
        self.suit = suit


class PictureCard(Card):
    class Kind(object):
        KING = "King"
        QUEEN = "Queen"
        JACK = "Jack"
        ACE = "Ace"

    kind = None

    @staticmethod
    def all_kinds():
        return (
            PictureCard.Kind.ACE,
            PictureCard.Kind.JACK,
            PictureCard.Kind.QUEEN,
            PictureCard.Kind.KING,
        )

    def __init__(self, suit, kind):
        self.suit = suit
        self.kind = kind

    def __str__(self):
        return "%s of %s" % (self.kind, self.suit)

    def __repr__(self):
        return str(self)


class NumberCard(Card):
    value = None

    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __str__(self):
        return "%d of %s" % (self.value, self.suit)

    def __repr__(self):
        return str(self)


class Deck(object):
    class Kind(object):
        CSM = "Continuous Shuffling Machine"
        SINGLE = "Single"
        MDS = "Multi-Deck Shoe"

    cards = []
    kind = None

    def all_kinds():
        return (Deck.Kind.CSM, Deck.Kind.SINGLE, Deck.Kind.MDS)

    @staticmethod
    def generate_decks(n):
        one_deck = []
        kinds = PictureCard.all_kinds()
        suits = Card.all_suits()
        for suit in suits:
            for number in range(2, 10):
                one_deck.append(NumberCard(suit, number))
            for kind in kinds:
                one_deck.append(PictureCard(suit, kind))

        cards = []
        for _ in range(1, n):
            cards += one_deck

        cards = cards[:52]

        return cards

    def __init__(self, kind):
        self.kind = kind

        # 1 if we're using a single deck, 6 if we're using a MDS,
        # this field is ignored if we're using a CSM
        self.num_decks = 1 if kind == Deck.Kind.SINGLE else 6
        self.cards = Deck.generate_decks(self.num_decks)

    def draw(self):
        if self.kind == self.Kind.CSM:
            return choice(self.cards)
        elif self.kind == self.Kind.SINGLE or self.kind == self.Kind.MDS:
            card = choice(self.cards)
            self.cards.remove(card)

            if len(self.cards) == 0:
                self.cards += Deck.single_deck(self.num_decks)

            return card
