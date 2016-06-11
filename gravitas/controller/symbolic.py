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

        # just return if there are no fields left
        if len(percievedField) == 0:
            return None

        # if only one stack left, return that one
        if len(percievedField) == 1:
            return percievedField[0].index 

        # if more than one choice left:

        # order options on card type
        tractors = [f for f in percievedField if f.card.getType() == Card.Type.tractor]
        normals = [f for f in percievedField if f.card.getType() == Card.Type.normal]
        repulsors = [f for f in percievedField if f.card.getType() == Card.Type.repulsor]

        #code from random, will be removed later
        # if there are cards left on the field, choose a stack
        if not len(percievedField) == 0:
            fieldOfChoice = random.choice(percievedField)
            # returns the index of the choosen stack
            return fieldOfChoice.index
        # end code
        return None

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        """chooses mainly on player-direction and cardtype. It does not take into account
            the cardNames (and thus playing-timing) or more complex ship-configurations
            or one-step-ahead-strategies"""

        # get player hand
        hand = self.player.getHand()

        # on empty hand
        if len(hand) == 0:
            return None

        # on 1 card in hand, play only card left
        if len(hand) == 1:
            return hand[0]

        # on more cards, make a choice between them

        # order options on card type
        tractors = [c for c in hand if c.getType() == Card.Type.tractor]
        normals = [c for c in hand if c.getType() == Card.Type.normal]
        repulsors = [c for c in hand if c.getType() == Card.Type.repulsor]

        # find closest ship
        targetName = state.getTarget(self.player.getName())

        # if no closest ship, the player is Stuck
        if targetName is None:
            # if available, try to play a tractor
            if len(tractors) > 0:
                return tractors[0]
            # otherwise, just play some card
            else:
                return random.choice(hand)

        # there is a closest ship: find moving direction  
        target = state.getShip(targetName).ship
        distance = target.getPos() - self.player.getPos()

        # moving forward...
        if distance > 0:
            # so choose highest-value normal card
            if len(normals) > 0:
                orderedNormals = sorted(normals, key = lambda x: x.getValue() )
                return orderedNormals[0]
            # if there are no normal cards, use tractor or lowest repulsor
            else:
                if len(tractors) > 0:
                    # use a tractor (does not mather which one since they are similar)
                    return tractors[0]
                # since then hand is not empty, there are only repulsors left
                else:
                    # chooce lowest repulsor
                    orderedRepulsors = sorted(repulsors, key = lambda x: -x.getValue() )
                    return orderedRepulsors[0]

        # moving backward...
        else: # if distance < 0:
            # so choose highest-value repulsor card
            if len(repulsors) > 0:
                orderedRepulsors = sorted(repulsors, key = lambda x: x.getValue() )
                return orderedRepulsors[0]
            # if there are no repulsor cards, use tractor or lowest normal
            else:
                if len(tractors) > 0:
                    # use a tractor (does not mather which one since they are similar)
                    return tractors[0]
                # since then hand is not empty, there are only normals left
                else:
                    # chooce lowest normal
                    orderedNormals = sorted(normals, key = lambda x: -x.getValue() )
                    return orderedNormals[0]

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean.
        Right now the choice is rather egocentric; no other-player-bullying is done."""

        # get closest ship
        targetName = state.getTarget(self.player.getName())

        if targetName is None:
            # player is stuck, don't waste ES!
            return False

        if self._playedCard.getType() == Card.Type.tractor:
            # choice of using ES with tractor cardType is complex...so dont
            return False

        # distance to closest ship (sign equals direction)
        target = state.getShip(targetName).ship
        distance = target.getPos() - self.player.getPos()
        
        if distance < 0 and self._playedCard.getType() == Card.Type.normal:
            # going  in normal direction with closest ship just behind you: use ES
            return True
        
        if distance > 0 and self._playedCard.getType() == Card.Type.repulsor:
            # getting repulsed with closest ship just behind you: use ES
            return True

        # return default
        return False

    def announceWinner(self, state):
        """Function that updates the PC after the last turn"""
        return None
        
    def informReveal(self, cards):
        """The definitive set of played cards in a round are shown to the player"""
        self.log.info("Random ai informed about %s" % cards)
        self._reveal = cards
        self._playedCard = [c for c in cards if cards[c] == self.player.getName()][0] # find unique card owned by player

    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        return False