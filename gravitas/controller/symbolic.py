"""A symbolic AI that forms decisions by using a decision tree."""

import random
from .interface import IPlayerController
from model.card import Card

class SymbolicAI_PC(IPlayerController):
    """player controller that returns resolutes its choices using a decision tree.
        It is called symbolic because it is not actually an AI"""
    def __init__(self, player, args,container):
        super().__init__(player,args)

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        """RANDOM choice"""
        
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()

        #code from random
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = random.choice(percievedField)
            # returns the index of the choosen stack
            return fieldOfChoice[0]
        # end code
        return None

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        """RANDOM choice"""

        # get closest ship
        target = state.getShip(state.getTarget(self.player.getName())).ship
        hand = self.player.getHand()

        # code from random
        if not len(hand) == 0:
            cardOfChoice = random.choice(hand)
            # returns the choosen card here
            return cardOfChoice
        # end code

        return None

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean.
        Right now the choice is rather egocentric; no other-player-bullying is done."""

        # get closest ship
        target = state.getShip(state.getTarget(self.player.getName())).ship

        if target is None:
            # player is stuck, don't waste ES!
            return False

        if self._playedCard.getType() == Card.Type.tractor:
            # choice of using ES with tractor cardType is complex...so dont
            return False

        # distance to closest ship (sign equals direction)
        distance = target.getPos() - self.player.getPos()
        
        if distance < 0 and self._playedCard.getType() == Card.Type.normal:
            # going  in normal direction with closest ship just behind you: use ES
            return True
        
        if distance > 0 and self._playedCard.getType() == Card.Type.repulsor:
            # getting repulsed with closest ship just behind you: use ES
            return True

        # return default
        return False

    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        return False
        
    def informReveal(self, cards):
        """The definitive set of played cards in a round are shown to the player"""
        self.log.info("Random ai informed about %s" % cards)
        self._reveal = cards
        self._playedCard = [c for c in cards if cards[c] == self.player.getName()][0] # find unique card owned by player

