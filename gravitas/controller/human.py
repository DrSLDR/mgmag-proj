"""This file contains the interface of the playerController, and the PC_types 
deriving from it. Currently the existing types are
 - The Human PC, which poll the choices this player makes from the gui
 - The Random AI PC, which makes a random choice"""

from human_player import HumanPlayer

from .interface import IPlayerController

class Human_PC(IPlayerController):
    """Human player Controller, that calls to the GUI for resolution of its functions"""
    def __init__(self, player, args,container):
        super().__init__(player,args)
        self.humanPlayerGui = HumanPlayer(self.player.getName(),container)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()
        selectedStackIndex = self.humanPlayerGui.decisionMaking_Drafting(percievedField)
        if selectedStackIndex is not None:
            fieldOfChoice = percievedField[selectedStackIndex]
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
            #return choice
            return cardOfChoice
        else:
            # returns None as long as no choice is made
            return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        doesPlayES = self.humanPlayerGui.decisionMaking_EmergencyStop()
        if doesPlayES is not None:        
            #return choice
            return doesPlayES
        else:
            # returns None as long as no choice is made
            return None
    
    def isHuman(self):
        """The board need to be able to find the human player, which this function will help with"""
        return True
