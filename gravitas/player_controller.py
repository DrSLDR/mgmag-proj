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
    def pollDraft(self, state):
        # returns None because it is an abstract function
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self, state):
        # returns None because it is an abstract function
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollEmergencyStop(self, state):
        # returns None because it is an abstract function
        return None

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        # returns None because it is an abstract function
        return None

class RandomAI_PC(IPlayerController):
    """player controller that returns random choices as resolution to its functions"""
    def __init__(self, player, args,container,app):
        super().__init__(player,args)

    """Function that returns the choice of a stack from the draw field"""
    def pollDraft(self, state):
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = random.choice(percievedField)
            print("Random AI "+self.player.getName()+" drew from field "+str(fieldOfChoice[1]))
            # returns the index of the choosen stack
            return fieldOfChoice[0]

        print("Oops, you are trying to choose a stack from an empty field") 
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self, state):
        hand = self.player.getHand()
        if not len(hand) == 0:
            cardOfChoice = random.choice(hand)
            print("Random AI "+self.player.getName()+" played card "+str(cardOfChoice))
            # returns the choosen card here
            return cardOfChoice

        print("Oops, you are trying to play a card from an empty hand")
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollEmergencyStop(self, state):
        doesPlayEmergencyStop = random.choice([True, False])
        if(doesPlayEmergencyStop):
            print("Random AI "+self.player.getName()+" DID play emergency stop")
        else:
            print("Random AI "+self.player.getName()+" did NOT play emergency stop")
        #return choice
        return doesPlayEmergencyStop
        
class Human_PC(IPlayerController):
    """Human player Controller, that calls to the GUI for resolution of its functions"""
    def __init__(self, player, args,container,app):
        super().__init__(player,args)
        import human_player
        self.humanPlayerGui = human_player.HumanPlayer(self.player.getName(),container,app)

    """Function that returns the choice of a stack from the draw field"""
    def pollDraft(self, state):
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()

        # TODO: implement choosing a card from the draw field
        selectedStackIndex = self.humanPlayerGui.decisionMaking_Drafting(percievedField)
        if not len(percievedField) == 0:
            # returns the index of the choosen stack
            fieldOfChoice = percievedField[selectedStackIndex] # stub: first stack
            print("Human "+self.player.getName()+" drew from field "+str(fieldOfChoice[1]))
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        # returns None as long as no choice is made
        return None

    """Function that returns which card the PC want to play"""
    def pollPlay(self, state):
        # chooses a card from the players hand
        hand = self.player.getHand()
        if not len(hand) == 0:
            # TODO: implement choosing a card from the hand
            #cardOfChoice = hand[0] # stub: default first card
            cardOfChoice = self.humanPlayerGui.decisionMaking_Playing(hand,
                                                                      self.player.canEmergencyStop())
            print("Human "+self.player.getName()+" played card "+str(cardOfChoice))
            #return choice
            return cardOfChoice
        else:
            print("Oops, you are trying to play a card from an empty hand")

        # returns None as long as no choice is made
        return None

    """Function that returns the choice of using the emergency stop as a boolean"""
    def pollEmergencyStop(self, state):
        # TODO: implement choosing to use the ES or not
        #doesPlayES = False # stub: default False
        doesPlayES = self.humanPlayerGui.decisionMaking_EmergencyStop()
            
        if(doesPlayES):
            print("Human "+self.player.getName()+" DID play emergency stop")
        else:
            print("Human "+self.player.getName()+" did NOT play emergency stop")
        #return choice
        return doesPlayES

        # returns None as long as no choice is made
        return None
    
