from __future__ import division, print_function
from pprint import pprint, pformat

from random import choice

# ---- #
# util #
# ---- #


def removeArrayObjectElem(arr, obj):
    d = dict(obj)
    i = 0
    for elem in arr:
        if dict(elem) == d:
            return arr.pop(i)
        i += 1
    raise Exception("Element not found in array")


def noneOrStr(obj):
    return "None" if obj is None else str(obj)


# ------- #
# CLASSES #
# ------- #

# ---- #
# card #
# ---- #


class Suit(object):
    SPADES = "Spades"
    CLUBS = "Clubs"
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"


SUITS = (Suit.SPADES, Suit.CLUBS, Suit.HEARTS, Suit.DIAMONDS)


def make_card(suit):
    return {"type": "card", "suit": suit}


class PictureCardKind(object):
    KING = "King"
    QUEEN = "Queen"
    JACK = "Jack"
    ACE = "Ace"


PICTURE_CARD_KINDS = (
    PictureCardKind.KING,
    PictureCardKind.QUEEN,
    PictureCardKind.JACK,
    PictureCardKind.ACE,
)


def make_picture_card(suit, kind):
    card = make_card(suit)
    card["type"] = "picture_card"
    card["kind"] = kind
    card["value"] = 11 if kind == PictureCardKind.ACE else 10
    return card


def make_number_card(suit, value):
    card = make_card(suit)
    card["type"] = "number_card"
    card["value"] = value
    return card


def card_repr(card):
    return "%s of %s" % (
        card["kind"] if card["type"] == "picture_card" else card["value"],
        card["suit"],
    )


def score_hand(hand):
    score = 0
    aces = 0
    for card in hand:
        if card.get("kind", None) == PictureCardKind.ACE:
            # Ace
            score += card["value"]
            aces += 1
        else:
            score += card["value"]

    while score > 21 and aces > 0:
        score -= 10
        aces -= 1
    return score


# ---- #
# deck #
# ---- #


class DeckKind(object):
    CSM = "Continuous Shuffling Machine"
    SINGLE = "Single Deck"
    MDS = "Multi-Deck Shoe"


DECK_KINDS = (DeckKind.CSM, DeckKind.SINGLE, DeckKind.MDS)


def populate_decks(n):
    one_deck = []
    for suit in SUITS:
        for number in range(2, 11):
            one_deck.append(make_number_card(suit, number))
        for kind in PICTURE_CARD_KINDS:
            one_deck.append(make_picture_card(suit, kind))

    cards = []
    for _ in range(n):
        cards += one_deck

    cards = cards[:52]
    return cards


def make_deck(kind, mds_deck_count=6):
    num_decks = 1 if kind == DeckKind.SINGLE else mds_deck_count
    return {
        "type": "deck",
        "kind": kind,
        "num_decks": num_decks,
        "cards": populate_decks(num_decks),
    }


def draw_from_deck(deck):
    if deck["kind"] == DeckKind.CSM:
        return choice(deck["cards"])
    elif deck["kind"] == DeckKind.SINGLE or deck["kind"] == DeckKind.MDS:
        card = choice(deck["cards"])
        removeArrayObjectElem(deck["cards"], card)

        if len(deck["cards"]) == 0:
            deck["cards"] += populate_decks(deck["num_decks"])
        return card


def deck_repr(deck):
    return "[%d] %s" % (len(deck["cards"], deck["kind"]))


# ---------- #
# game state #
# ---------- #


class GameStage(object):
    NOT_STARTED = "Not started"
    PLAYING = "Playing"
    ROUND_FINISHED = "Round finished"
    OUT_OF_MONEY = "Out of money"


class GameResult(object):
    DEALER_WINS = "Dealer wins"
    TIE = "Tie"
    PLAYER_BUSTS = "Player busts"
    DEALER_BUSTS = "Dealer busts"
    PLAYER_WINS = "Player wins"
    PLAYER_BJ = "Player blackjack"
    DEALER_BJ = "Dealer blackjack"


def game_reset_round_state(game):
    game["stage"] = GameStage.NOT_STARTED
    game["result"] = None
    game["player_hand"] = []
    game["hole_card"] = None
    game["dealer_hand"] = []
    game["player_standing"] = False
    game["dealer_standing"] = False
    game["player_turn"] = True
    return game


def make_game(deck, starting_balance):
    return game_reset_round_state(
        {
            "type": "game",
            "deck": deck,
            "balance": starting_balance,
            "bet": starting_balance / 10,
        }
    )


def player_score(game):
    return score_hand(game["player_hand"])


def dealer_score(game):
    return score_hand([game["hole_card"]] + list(game["dealer_hand"]))


def game_deal(game, bet):
    if game["stage"] == GameStage.ROUND_FINISHED:
        game = game_reset_round_state(game)
    elif game["stage"] != GameStage.NOT_STARTED:
        raise Exception("Invalid game stage")

    game["bet"] = bet
    game["player_hand"] = [draw_from_deck(game["deck"]), draw_from_deck(game["deck"])]
    game["hole_card"] = draw_from_deck(game["deck"])
    game["dealer_hand"] = [draw_from_deck(game["deck"])]
    game["stage"] = GameStage.PLAYING

    # Evaluate natural blackjack
    player_bj = 21 == player_score(game)
    dealer_bj = 21 == dealer_score(game)
    if player_bj or dealer_bj:
        game["stage"] = GameStage.ROUND_FINISHED
        if player_bj and dealer_bj:
            game["result"] = GameResult.TIE
        elif player_bj and not dealer_bj:
            game["balance"] += 1.5 * game["bet"]
            game["result"] = GameResult.PLAYER_BJ
        elif dealer_bj and not player_bj:
            game["balance"] -= game["bet"]
            game["result"] = GameResult.DEALER_BJ
    return game


def game_repr(game):
    return (
        "Stage: %s" % game["stage"]
        + "\nResult: %s" % game["result"]
        + "\nBalance: $%d" % game["balance"]
        + "\nBet: $%d" % game["bet"]
        + "\nPlayer turn? %s" % game["player_turn"]
        + "\nPlayer standing? %s" % game["player_standing"]
        + "\nDealer standing? %s" % game["dealer_standing"]
        + "\n"
        + game_hand_repr(game)
    )


def game_hand_repr(game):
    return "Player hand: %s %s" % (
        player_score(game),
        map(card_repr, game["player_hand"]),
    ) + "\nDealer hand: %s <(%s)> | %s" % (
        dealer_score(game),
        card_repr(game["hole_card"]),
        map(card_repr, game["dealer_hand"]),
    )


def game_assert_playing(game):
    if game["stage"] != GameStage.PLAYING:
        raise Exception("Invalid game stage")


def game_assert_first_round(game):
    game_assert_playing(game)
    if len(game["player_hand"]) != 2:
        raise Exception("Not first round")


def game_assert_player_turn(game):
    if not game["player_turn"]:
        raise Exception("It is not the player's turn")
    if game["player_standing"]:
        raise Exception("Player is standing")


def game_assert_not_player_turn(game):
    if game["player_turn"]:
        raise Exception("It is the player's turn")


def game_assert_scores_lte_21(game):
    p = player_score(game)
    d = dealer_score(game)
    if p > 21 or d > 21:
        raise Exception("Player or dealer busted")
    return (p, d)


def game_action_surrender(game):
    game_assert_playing(game)
    game_assert_first_round(game)
    game_assert_player_turn(game)

    game["balance"] -= game["bet"] / 2
    game["stage"] = GameStage.ROUND_FINISHED
    game["result"] = GameResult.DEALER_WINS
    game["player_turn"] = False
    return game


def game_action_double_down(game):
    game_assert_playing(game)
    game_assert_first_round(game)
    game_assert_player_turn(game)

    game["bet"] *= 2
    game["player_hand"].append(draw_from_deck(game["deck"]))
    game["player_standing"] = True
    game["player_turn"] = False

    game_check_both_standing(game)

    return game


def game_action_stand(game):
    game_assert_playing(game)
    game_assert_player_turn(game)

    game["player_standing"] = True
    game["player_turn"] = False

    game_check_both_standing()

    return game


def game_check_both_standing(game):
    game_assert_playing(game)
    p, d = game_assert_scores_lte_21(game)
    if game["dealer_standing"] and game["player_standing"]:
        # We don't need to check if anyone has a natural blackjack;
        # that's handled during the initial deal logic.
        # We also don't need to check if the player or dealer have
        # busted, that's handled in the hit logic

        # We know that both scores are <= 21
        if p > d:
            game["balance"] += game["bet"]
            game["stage"] = GameStage.ROUND_FINISHED
            game["result"] = GameResult.PLAYER_WINS
        elif d > p:
            game["balance"] -= game["bet"]
            game["stage"] = GameStage.ROUND_FINISHED
            game["result"] = GameResult.DEALER_WINS
        elif d == p:
            game["stage"] = GameStage.ROUND_FINISHED
            game["result"] = GameResult.TIE

    return game


def game_action_hit_player(game):
    game_assert_playing(game)
    game_assert_player_turn(game)

    game["player_hand"].append(draw_from_deck(game["deck"]))

    if player_score(game) > 21:
        game["balance"] -= game["bet"]
        game["stage"] = GameStage.ROUND_FINISHED
        game["result"] = GameResult.PLAYER_BUSTS
    elif player_score(game) == 21:
        game["player_standing"] = True
        game_check_both_standing()

    game["player_turn"] = False
    return game


def game_action_hit_dealer(game):
    game_assert_playing(game)
    game_assert_not_player_turn(game)

    game["dealer_hand"].append(draw_from_deck(game["deck"]))

    if dealer_score(game) > 21:
        game["balance"] += game["bet"]
        game["stage"] = GameStage.ROUND_FINISHED
        game["result"] = GameResult.DEALER_BUSTS
    elif dealer_score(game) >= 17:
        game["dealer_standing"] = True
        game_check_both_standing()

    game["player_turn"] = True
    return game
