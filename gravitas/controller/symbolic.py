"""A symbolic AI that forms decisions by using a decision tree."""

import random
from .interface import IPlayerController

class SymbolicAI_PC(IPlayerController):
    """player controller that returns resolutes its choices using a decision tree.
        It is called symbolic because it is not actually an AI"""
    def __init__(self, player, args,container):
        super().__init__(player,args)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = random.choice(percievedField)
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        print("Oops, you are trying to choose a stack from an empty field") 
        return None

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        hand = self.player.getHand()
        if not len(hand) == 0:
            cardOfChoice = random.choice(hand)
            # returns the choosen card here
            return cardOfChoice
        print("Oops, you are trying to play a card from an empty hand")
        return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""

        # get closest ship and its distance to the player
        target = state.getTarget(self.player.getName())
        if target is None:
            # player is stuck, don't waste ES!
            return False

        if self._playerCard.getType() == Card.Type.tractor:
            # choosing ES with this cardType is complex...
            return False

        # player can move: determine use of ES
        distance = target.getPos() - self.player.getPos()
        if distance < 0:
            return True


    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        return False
        
    def informReveal(self, cards):
        """The definitive set of played cards in a round are shown to the player"""
        self.log.info("Random ai informed about %s" % cards)
        self._reveal = cards
        self._playedCard = [c for c in cards if c[1] == self._player.getName()][0]

