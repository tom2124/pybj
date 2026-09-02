from __future__ import division
from __builtins__ import print

from random import choice

# ------- #
# CLASSES #
# ------- #


class Card(object):
    value = None

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
            PictureCard.Kind.KING,
            PictureCard.Kind.QUEEN,
            PictureCard.Kind.JACK,
            PictureCard.Kind.ACE,
        )

    def __init__(self, suit, kind):
        self.suit = suit
        self.kind = kind
        self.value = 11 if self.kind == PictureCard.Kind.ACE else 10

    def __str__(self):
        return "%s of %s" % (self.kind, self.suit)

    def __repr__(self):
        return str(self)


class NumberCard(Card):
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


class GameStage(object):
    NOT_STARTED = -1
    PLAYING = 0
    ROUND_FINISHED = 1
    OUT_OF_MONEY = 2


class GameResult(object):
    DEALER_WINS = -1
    TIE = 0
    PLAYER_BUSTS = 1
    DEALER_BUSTS = 2
    PLAYER_WINS = 3
    PLAYER_BJ = 4
    DEALER_BJ = 5


class GameState(object):
    balance = 0
    game_result = None

    def reset_round_state(self):
        self.stage = GameStage.NOT_STARTED
        self.game_result = None
        self.player_hand = []
        self.hole_card = None
        self.dealer_hand = []
        self.player_standing = False
        self.player_turn = True

    def __init__(self, deck, starting_balance):
        self.deck = deck
        self.balance = starting_balance
        self.reset_round_state()

    def deal(self, bet):
        if self.stage == GameStage.ROUND_FINISHED:
            self.reset_round_state()
        elif self.stage != GameStage.NOT_STARTED:
            raise Exception("Invalid game stage")

        self.bet = bet
        self.player_hand = [self.deck.draw(), self.deck.draw()]
        self.hole_card = self.deck.draw()
        self.dealer_hand = [self.deck.draw()]
        self.stage = GameStage.PLAYING

        # Evaluate natural blackjack
        player_bj = 21 == self.player_score
        dealer_bj = 21 == self.dealer_score
        if player_bj or dealer_bj:
            self.stage = GameStage.ROUND_FINISHED
            if player_bj and dealer_bj:
                self.game_result = GameResult.TIE
            elif player_bj and not dealer_bj:
                self.balance += 1.5 * self.bet
                self.game_result = GameResult.PLAYER_BJ
            elif dealer_bj and not player_bj:
                self.balance -= self.bet
                self.game_result = GameResult.DEALER_BJ

    @staticmethod
    def score_hand(hand):
        score = 0
        aces = 0
        for card in hand:
            if isinstance(card, PictureCard) and card.kind == PictureCard.Kind.ACE:
                # Ace
                score += card.value
                aces += 1
            else:
                score += card.value

        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        return score

    @property
    def player_score(self):
        return self.score_hand(self.player_hand)

    @property
    def dealer_score(self):
        return self.score_hand([self.hole_card] + self.dealer_hand)

    def print_hands(self):
        print("Player: %s %s" % (self.player_score, self.player_hand))
        print(
            "Dealer: %s [%s] | %s"
            % (self.dealer_score, self.hole_card, self.dealer_hand)
        )

    def assert_playing(self):
        if self.stage != GameStage.PLAYING:
            raise Exception("Invalid game stage")

    def assert_first_round(self):
        if len(self.player_hand) != 2:
            raise Exception("Not first round")

    def assert_player_turn(self):
        if not self.player_turn:
            raise Exception("It is not the player's turn")
        if self.player_standing:
            raise Exception("Player is standing")

    def action_surrender(self):
        self.assert_playing()
        self.assert_first_round()
        self.assert_player_turn()

        self.balance -= self.bet / 2
        self.stage = GameStage.ROUND_FINISHED
        self.game_result = GameResult.DEALER_WINS

    def action_double_down(self):
        self.assert_playing()
        self.assert_first_round()
        self.assert_player_turn()

        self.bet *= 2
        self.player_hand.append(self.deck.draw())

    def action_stand(self):
        self.assert_player_turn()
        self.assert_playing()

        self.player_standing = True

    def action_hit_player(self):
        self.assert_playing()
        self.assert_player_turn()

        self.player_hand.append(self.deck.draw())

        if self.player_score > 21:
            self.balance -= self.bet
            self.stage = GameStage.ROUND_FINISHED
            self.game_result = GameResult.PLAYER_BUSTS

        # TODO: if the player hits 21 or under, we need to let at least one more dealer turn go ahead and potentially more player turns go ahead
