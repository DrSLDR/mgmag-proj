"""This file contains the interface of the playerController, and the PC_types 
deriving from it. Currently the existing types are
 - The Human PC, which poll the choices this player makes from the gui
 - The Random AI PC, which makes a random choice"""

import pygame
import random

class IPlayerController():
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""

    def __init__(self, player, args):
        self.player = player

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        return None # returns None because it is an abstract function

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        return None # returns None because it is an abstract function

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        return None # returns None because it is an abstract function

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        return None # returns None because it is an abstract function

class RandomAI_PC(IPlayerController):
    """player controller that returns random choices as resolution to its functions"""
    def __init__(self, player, args,container):
        super().__init__(player,args)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
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

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        hand = self.player.getHand()
        if not len(hand) == 0:
            cardOfChoice = random.choice(hand)
            print("Random AI "+self.player.getName()+" played card "+str(cardOfChoice))
            # returns the choosen card here
            return cardOfChoice
        print("Oops, you are trying to play a card from an empty hand")
        return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        doesPlayEmergencyStop = random.choice([True, False])
        if(doesPlayEmergencyStop):
            print("Random AI "+self.player.getName()+" DID play emergency stop")
        else:
            print("Random AI "+self.player.getName()+" did NOT play emergency stop")
        #return choice
        return doesPlayEmergencyStop
        
class Human_PC(IPlayerController):
    """Human player Controller, that calls to the GUI for resolution of its functions"""
    def __init__(self, player, args,container):
        super().__init__(player,args)
        import human_player
        self.humanPlayerGui = human_player.HumanPlayer(self.player.getName(),container)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()
        selectedStackIndex = self.humanPlayerGui.decisionMaking_Drafting(percievedField)
        if selectedStackIndex is not None:
            fieldOfChoice = percievedField[selectedStackIndex]
            print("Human "+self.player.getName()+" drew from field "+str(fieldOfChoice[1]))
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        else:
            # returns None as long as no choice is made
            return None

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        # chooses a card from the players hand
        hand = self.player.getHand()
        cardOfChoice = self.humanPlayerGui.decisionMaking_Playing(hand,
                                                                      self.player.canEmergencyStop())
        if cardOfChoice is not None:
            print("Human "+self.player.getName()+" played card "+str(cardOfChoice))
            #return choice
            return cardOfChoice
        else:
            # returns None as long as no choice is made
            return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        doesPlayES = self.humanPlayerGui.decisionMaking_EmergencyStop()
        if doesPlayES is not None:        
            if(doesPlayES):
                print("Human "+self.player.getName()+" DID play emergency stop")
            else:
                print("Human "+self.player.getName()+" did NOT play emergency stop")
            #return choice
            return doesPlayES
        else:
            # returns None as long as no choice is made
            return None
    
