"""Random AI a random reference implementation."""

import random
from .interface import IPlayerController

class RandomAI_PC(IPlayerController):
    """player controller that returns random choices as resolution to its functions"""
    def __init__(self, player, args,container):
        super().__init__(player,args)
        self.rng = random.Random()

    def seed(self, withvar):
        self.rng.seed(withvar)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = self.rng.choice(percievedField)
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        print("Oops, you are trying to choose a stack from an empty field") 
        return None

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        hand = self.player.getHand()
        if not len(hand) == 0:
            cardOfChoice = self.rng.choice(hand)
            # returns the choosen card here
            return cardOfChoice
        print("Oops, you are trying to play a card from an empty hand")
        return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        doesPlayEmergencyStop = self.rng.choice([True, False])
        #return choice
        return doesPlayEmergencyStop

    def announceWinner(self, state):
        """Function that updates the PC after the last turn"""
        return None
        
    def informReveal(self, cards):
        self.log.info("Random ai informed about %s" % cards)
        
    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        return False

class RandomIgnoreEmergency(RandomAI_PC):
    def pollEmergencyStop(self, state):
        return False
