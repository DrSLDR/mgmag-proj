"""Module containing ship and player class"""
from card import Card

"""Ship class. Represents a ship on the game board"""
class Ship:

    """Nested class acting as enumeration over ship colors"""
    class Color:
        gray = 0
        red = 1
        blue = 2
        yellow = 3
        green = 4

    """Constructs the ship. Starting position can optionally be set"""
    def __init__(self, color=0, pos=0):
        self._pos = pos
        self._color = color

    """Getters. Direct access to instance variables is still bad mojo."""
    def getPos(self):
        return self._pos

    def getColor(self):
        return self._color

    """Distance-to function. Returns absolute-valued distance to given ship."""
    def distanceTo(self, ship):
        return abs(self._pos - ship.getPos())

    """Direction-to function. Returns 1 if the given ship is ahead or -1 if it
    is behind. If both ships are in the singularity, it returns 0."""
    def directionTo(self, ship):
        if self._pos - ship.getPos() > 0:
            return -1
        elif self._pos == ship.getPos():
            return 0
        else:
            return 1

    """Move function. Adds the given value to the ship's position. Tests to make
    sure that the position isn't outside of the board in either direction."""
    def move(self, value):
        self._pos = self._pos + value
        if self._pos > 55:
            self._pos = 55
        elif self._pos < 0:
            self._pos = 0

##### END OF SHIP CLASS ########################################################
        
"""Player class. Represents a ship with a player"""
class Player(Ship):

    """Constructs the player. Name can be any string"""
    def __init__(self, color, name):
        super().__init__(color)
        self._name = name
        self._hand = []

    """Getters"""
    def getName(self):
        return self._name
        
    def getHand(self):
        return self._hand
