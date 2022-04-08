#! /usr/bin/env python3

import random
import os

from cards import *

debug = False
trace = False
testing = False

No_One_Won = 0
Player_Won = 1
Player_Lost = 2

def user_option (can_bet=False, can_deal=False, can_stand=True, can_hit=False, can_buy_insurance=False, can_double_down=False, can_split=False):

    while True:
        valid_options = []

        print ("What would you like to do: ")
    
        if can_bet:
            print ("    (B)et")
            valid_options += "b"
    
        if can_deal:
            print ("    d(E)al")
            valid_options += "e"
    
        if can_buy_insurance:
            print ("    I)nsurance")
            valid_options += "i"
    
        if can_split:
            print ("    S(p)lit")
            valid_options += "s"
            
        if can_double_down:
            print ("    (D)ouble Down")
            valid_options += "d"
    
        if can_hit:
            print ("    (H)it")
            valid_options += "h"

        if can_stand:
            print ("    (S)tand")
            valid_options += "x"
    
        option = input ("? ")

        if len(option) == 0:
            continue

        option = option [0].lower ()

        if option in valid_options:
            return option

        if not can_bet and option == "b":
            print ("You cannot bet now")
            continue
        
        if not can_deal and option == "e":
            print ("Cannot redeal now")
            continue
        
        if not can_buy_insurance and option == "i":
            print ("You cannot buy insurance now")
            continue
        
        if not can_double_down and option == "d":
            print ("You cannot double down now")
            continue
        
        if not can_split and option == "p":
            print ("You cannot double down now")
            continue

        if not can_hit and option == "h":
            print ("You cannot hit now")
            continue

        print ("Please chose a valid option\n")
        
    return option


def play(deck=None):
    if debug: print(f"play()")

    global testing
    global player_bank
 
    player_bank = 1000
    print(f"Player Bank: ${player_bank}")

    if deck is None:
        deck = build_deck()
    else:
        testing = True

    deck.pop(0) # burn a card

    keep_playing = True

    while keep_playing:

        if not testing:
            os.system("clear")

        print(f"\nPlayer starting bank: ${player_bank}")
        play_hand (deck)

        print(f"Player Bank: ${player_bank}\n")

        if testing: break

        keep_playing = not input("Keep playing? ").lower()[0] != "y"

    if not testing:
        print("So long...\n")


def play_hand (deck):

    global player_bank

    player_bet = 100

    while True:
        player_choice = user_option(can_bet=True, can_deal=True, can_stand=False).lower()
    
        if player_choice == "b":
    
            while True:
        
                try:
                    player_bet = float(input("Enter your bet: $ ") or player_bet)
        
                except ValueError:
                    print("> Error: Enter a valid number\n")
                    continue
        
                break
    
        if player_choice == "e": break

    print(f"\nPlayer Bet: ${player_bet}\n")

    player_hand = []
    dealer_hand = []

    for i in range(2):

        if len(deck) == 0: raise Exception("Empty deck logic is not implemented yet")
        
        player_hand.append(deck.pop(0))
    
        if len(deck) == 0: raise Exception("Empty deck logic is not implemented yet")
        
        dealer_hand.append(deck.pop(0))

    if testing:
        print ("Dealer's cards")
        print ("    face down card")
        print_card (dealer_hand[1])
        print ()

    else:
        display_hand ("Dealer", dealer_hand, hide_first_card=False)

    display_hand ("Player", player_hand)

    insurance_bet = 0.0

    player_choice = None

    if is_ace (dealer_hand[1]):
        player_choice = user_option(can_hit=True, can_double_down=True, can_buy_insurance=True, can_split=(rank_of(player_card[0] == rank_of(player_card[1])))).lower()

        if player_choice == "i":
            if trace: print("player chose to buy insurance")

            player_choice = None

            while True:
                print(f"initial bet: ${player_bet}")

                try:
                    insurance_bet = float(input("How much insurance amount: "))

                except:
                    continue
                
                if insurance_bet > (player_bet/2):
                    print("you may only bet up to 1/2 of your initial bet")
                    continue

                break

        if not is_blackjack (dealer_hand):
            print ("Dealer does not have Blackjack; Player loses insurance bet\n")
            player_bank -= insurance_bet

    if is_blackjack(dealer_hand):
        print ("Dealer has Blackjack", end="")

        winnings = 0
        
        if insurance_bet > 0.0:
            print ("; Player wins insurance bet")

        print ()

        player_bank += 2*insurance_bet
        winnings += 2*insurance_bet

        if is_blackjack (player_hand):
            print ("Player also Blackjack; Player wage is returned\n")
        else:
            print ("Player doesn't have Blackjack; Player loses\n")
            player_bank -= player_bet
            winnings -= player_bet

        return winnings

    if total(player_hand) == 21:
        player_bank += 1.5 * player_bet
        return 1.5*player_bet - insurance_bet

    player_can_hit = True
    splittable = rank_of(player_hand[0]) == rank_of(player_hand[1])

    if player_choice is None:
        player_choice = user_option(can_hit=True, can_double_down=True, can_split=splittable)

    if player_choice == "d":
        print ("Player doubled his bet and gets a card")
        player_choice = None
        player_bet *= 2.0
        player_hand.append(deck.pop(0))

        display_hand("Player", player_hand)

        player_can_hit = False

    while player_can_hit:
        splittable = len (player_hand) == 2 and (rank_of(player_hand[0]) == rank_of(player_hand[1]))

        if player_choice is None:
            player_choice = user_option(can_hit=True, can_split=splittable)

        if player_choice == "s":
            player_choice = None
            print ("Player chose to stand")
            player_can_hit = False
            continue

        if player_choice == "h":
            player_choice = None
            card = deck.pop(0)
            print ("Player hits and gets the", end=" ")
            print_card (card, 0)

            player_hand.append(card)

            if total(player_hand) <= 21:
                display_hand ("Dealer", dealer_hand, hide_first_card=False)

            display_hand("Player", player_hand)

            if total(player_hand) > 21:
                player_can_hit = False
                continue

        if player_choice == "p":
            player_choice = None
            raise NotImplementedError("Splitting is not implemented yet. Please try again later.")

    if total(player_hand) > 21:
        print ("Player busts")
        player_bank -= player_bet
        return -(player_bet + insurance_bet)

    while total(dealer_hand) < 17:
        card = deck.pop(0)
        dealer_hand.append(card)

        print (f"Dealer hits and gets the", end=" ")
        print_card (card, 0)
        print ()

        display_hand("Dealer", dealer_hand)

    if total(dealer_hand) > 21:
        print ("Dealer busts")
        player_bank += player_bet
        return player_bet - insurance_bet

    result = evaluate_hands (dealer_hand, player_hand)

    if result == Player_Won:
        print ("Players has better hand, so player wins")
        player_bank += player_bet
        return  player_bet - insurance_bet

    if result == Player_Lost:
        print ("Dealer has better hand, so player loses")
        player_bank -= player_bet
        return -(player_bet + insurance_bet)

    print ("Push, so player get his wager back")
    return -insurance_bet


def evaluate_hands (dealer_hand, players_hand):
    if debug: print (f"evaluate_hands ({dealer_hand}, {players_hand}")

    print ()
    display_hand("Dealer", dealer_hand)

    if total(dealer_hand) > total(players_hand):
        return Player_Lost

    if total(dealer_hand) < total(players_hand):
        return Player_Won

    return No_One_Won


def build_deck(shuffle=True):
    if debug: print(f"build_deck({shuffle})")

    deck = []
    
    for suit in Suits:

        for rank in Ranks:
            card = (rank, suit)
            deck.append (card)

            if trace: print (card)

    if shuffle: 
        random.shuffle(deck)

    return deck


def is_ace (card): return card[Rank_Index] == Ace
def is_face_card (card): return card[Rank_Index] >= Jack and card[Rank_Index] <= King

def rank_of(card): return card[Rank_Index]

def value(card):
    if debug: print (f"value({card})")

    if is_ace (card): return 11

    if is_face_card (card): return 10

    return card[Rank_Index]


def total(hand):
    if debug: print (f"total({hand})")

    total = 0
    ace_count = 0

    for card in hand:
        if trace: print (f"    value: {card}")
        total += value(card)

        if is_ace (card): ace_count += 1

    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1

    return total


def is_blackjack (hand): return len(hand) == 2 and total(hand) == 21


def soft(hand, value):
    if debug: print (f"soft ({hand}, {value}")

    if len(hand) != 2 and total(hand) != value: return False
    
    return is_Ace(hand[0]) or is_Ace(hand[1])


def print_card(card, indent=4):
    
    print (" "*indent, end="")
    print (f"{Rank_Map[card[Rank_Index]]} of {Suit_Map[card[Suit_Index]]}")


def print_hand(player, hand):

    print (f"{player}'s cards")

    for card in hand:
        print_card (card)

    print(f"total: {total(hand)}\n")


def display_hand (player, hand, hide_first_card=False):

    if testing:
        print_hand(player, hand)
        return

    print (f"{player}'s hand")

    if not hide_first_card:
        lines = [ [] for i in range(9) ]
    
    else:
        hand = hand.copy()
        hand.pop (0)

        lines = [['┌─────────┐'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['│░░░░░░░░░│'],
                 ['└─────────┘']]

    for card in hand:
        space = " "
        suit = Suit_Symbols[card[Suit_Index]-1]

        if is_face_card (card) or is_ace(card):
            rank = Rank_Map[card[Rank_Index]][0]
        else:
            rank = str(card[Rank_Index])

            if len(rank) == 2:
                space = ""

        lines[0].append('┌─────────┐')
        lines[1].append('│{}{}       │'.format(rank, space))
        lines[2].append('│         │')
        lines[3].append('│         │')
        lines[4].append('│    {}    │'.format(suit))
        lines[5].append('│         │')
        lines[6].append('│         │')
        lines[7].append('│       {}{}│'.format(space, rank))
        lines[8].append('└─────────┘')

    result = []

    for index, line in enumerate(lines):
        result.append(''.join(lines[index]))

    print ('\n'.join(result))

    if not hide_first_card:
        print(f"total: {total(hand)}\n")
    else:
        print ()


if __name__ == "__main__":
    play()
