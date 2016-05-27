"""This file contains the Ship model and Player model"""
from .card import Card
from .ship import Ship
import copy

class Player(Ship):
    """Player class. Represents a ship with a player"""

    def __init__(self, color, name):
        """Constructs the player. Name can be any string"""
        super().__init__(color)
        self._name = name
        self._hand = []
        self._canEmergencyStop = True

    def addCards(self, pair):
        """Adds a pair of cards to the hand"""
        self._hand += list(pair)
    def playCard(self, card):
        """Removes a played card from the hand"""
        self._hand.remove(card)

    def useEmergencyStop(self):
        """Sets the Emergency Stop as used"""
        self._canEmergencyStop = False
    def resetEmergencyStop(self):
        """Resets the Emergency Stop as usable"""
        self._canEmergencyStop = True

    def getName(self):
        return self._name
    def getHand(self):
        return self._hand

    def canEmergencyStop(self):
        return self._canEmergencyStop
    def distanceToFinish(self):
        return 54 - self.getPos()

    def makeCensoredCopy(self):
        """Creates a censored copy of the player object, simply meaning a copy
        without hand info"""
        selfCopy = copy.copy(self)
        selfCopy._hand = []
        return selfCopy
        
    def __str__(self):
        return self.getName() + " (" + str(self.getPos()) + ")" 
    def __repr__(self):
        return self.__str__()

