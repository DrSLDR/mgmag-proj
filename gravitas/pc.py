import pygame
import random
from player import Player, Ship
from card import Card, Deck

"""This file contains the interface of the playerController, and the PC_types deriving from it. 
Currently the existing types are
 - The Human PC, which poll the choices this player makes from the gui
 - The Random AI PC, which makes a random choice"""


class IPlayerController():
    
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""
    def __init__(self, player, args):
        self.player = player

    """Function that returns the choice of a stack from the draw field"""
    def pollDraw(self, percievedField):
        # returns None because it is an abstract function
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self):
        # returns None because it is an abstract function
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollUseES(self):
        # returns None because it is an abstract function
        return None


class RandomAI_PC(IPlayerController):
    """player controller that returns random choices as resolution to its functions"""
    def __init__(self, player, args):
        super().__init__(player,args)

    """Function that returns the choice of a stack from the draw field"""
    def pollDraw(self, percievedField):
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = random.choice(percievedField)
            print("Random AI "+self.player.getName()+" drew from field "+str(fieldOfChoice[1]))
            # returns the index of the choosen stack
            return fieldOfChoice[0]

        print("Oops, you are trying to choose a stack from an empty field") 
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self):
        hand = self.player.getHand()
        if not len(hand) == 0:
            cardOfChoice = random.choice(hand)
            print("Random AI "+self.player.getName()+" played card "+str(cardOfChoice))
            # returns the choosen card here
            return cardOfChoice

        print("Oops, you are trying to play a card from an empty hand")
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollUseES(self):
        # only make a choise if the player has an emergency stop left
        if self.player.casES():
            doesPlayES = random.choice([True, False])
            if(doesPlayES):
                print("Random AI "+self.player.getName()+" DID play emergency stop")
            else:
                print("Random AI "+self.player.getName()+" did NOT play emergency stop")
            #return choice
            return doesPlayES
        else: 
            return False


class Human_PC(IPlayerController):
    """Human player Controller, that calls to the GUI for resolution of its functions"""
    def __init__(self, player, args):
        super().__init__(player,args)

    """Function that returns the choice of a stack from the draw field"""
    def pollDraw(self, percievedField):
        # TODO: implement choosing a card from the draw field
        if not len(percievedField) == 0:
            # returns the index of the choosen stack
            fieldOfChoice = percievedField[0] # stub: first stack
            print("Human "+self.player.getName()+" drew from field "+str(fieldOfChoice[1]))
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        # returns None as long as no choice is made
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self):
        # chooses a card from the players hand
        hand = self.player.getHand()
        if not len(hand) == 0:
            # TODO: implement choosing a card from the hand
            cardOfChoice = hand[0] # stub: default first card
            print("Human "+self.player.getName()+" played card "+str(cardOfChoice))
            #return choice
            return cardOfChoice
        else:
            print("Oops, you are trying to play a card from an empty hand")

        # returns None as long as no choice is made
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollUseES(self):
        # PC can choose to use ES if it is still available for this player
        if self.player.casES():
            # TODO: implement choosing to use the ES or not
            doesPlayES = False # stub: default False
            if(doesPlayES):
                print("Human "+self.player.getName()+" DID play emergency stop")
            else:
                print("Human "+self.player.getName()+" did NOT play emergency stop")
            #return choice
            return doesPlayES
        else: 
            return False

        # returns None as long as no choice is made
        return None
