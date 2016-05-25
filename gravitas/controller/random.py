"""Random AI a random reference implementation."""

import random
from .interface import IPlayerController

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
