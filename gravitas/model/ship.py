"""This file contains the Ship model and Player model"""
class Ship:
    """Represents a ship on the game board"""

    class Color:
        """enumeration over ship colors"""
        gray = 0
        red = 1
        blue = 2
        yellow = 3
        green = 4

    def __init__(self, color=0, pos=0):
        """Constructs the ship. Starting position can optionally be set"""
        self._pos = pos
        self._color = color

    def getPos(self):
        return self._pos
    def getColor(self):
        return self._color
    def getName(self):
        return "Hulk"

    def distanceTo(self, ship):
        """Returns absolute-valued distance to given ship."""
        return abs(self._pos - ship.getPos())

    def directionTo(self, ship):
        """Returns 1 if the given ship is ahead or -1 if it is behind. 
        If both ships are in the singularity, it returns 0."""
        if self._pos - ship.getPos() > 0:
            return -1
        elif self._pos == ship.getPos():
            return 0
        else:
            return 1

    def move(self, value):
        """Adds the given value to the ship's position. Tests to make
        sure that the position isn't outside of the board in either direction."""
        self._pos += value
        if self._pos > 54:
            self._pos = 54
        elif self._pos < 0:
            self._pos = 0

    def __str__(self):
        return self.getName() + " (" + str(self.getPos()) + ")" 
    def __repr__(self):
        return self.__str__()
