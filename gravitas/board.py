""" This file describes the board rendering aspect of the game
"""
from model import board

from collections import namedtuple
import math

Point=namedtuple('Point',['x','y'])
def _calcPosition(tileNumber):
    """
    In a number
    Out some coordinates (non scaled, just as a grid)
    """
    tileNumber = tileNumber + 1 # to start at 0
    # thanks: https://math.stackexchange.com/questions/163080/on-a-two-dimensional-grid-is-there-a-formula-i-can-use-to-spiral-coordinates-in
    # second anwser after spending more than 2 hours on the first.
    # hours wasted: 3
    # increase above number if you wanted to "improve" this code
    k=math.ceil((math.sqrt(tileNumber)-1)/2)
    t=2*k+1
    m=t**2 
    t=t-1

    if tileNumber>=m-t:
        return Point(x=k-(m-tileNumber),y=-k)
    m=m-t
    if tileNumber>=m-t:
        return Point(x=-k,y=-k+(m-tileNumber))
    m=m-t
    if tileNumber>=m-t:
        return Point(x=-k+(m-tileNumber),y=k)
    return Point(x=k,y=k-(m-tileNumber-t))

from model.player import Ship
class Renderer:
    """
    Renders a board
    """
    # redefine the ship colors as proper tuples.
    colors = {
        Ship.Color.gray: (60,60,60),
        Ship.Color.red: (204,0,0),
        Ship.Color.blue: (0,0,153),
        Ship.Color.yellow: (204,204,0),
        Ship.Color.green: (0,51,0),
    }

    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.borderpadding = 0.05
        def scale(num):
            return (num*(1-2*self.borderpadding))/math.sqrt(len(board.tiles))
        self.scale = Point(
            x=scale(screenSize.width),
            y=scale(screenSize.height)
        )

    def calcScreenPos(self, tileNumber):
        """Amends calcpostion with knowledge of the board"""
        pos = _calcPosition(tileNumber)
        pos = Point(
            x=pos.x*self.scale.x+self.screenSize.width*(0.5-self.borderpadding),
            y=pos.y*60+self.screenSize.height*(0.5-self.borderpadding))
        return pos

    def render(self, font, disp, gamestate):
        import pygame
        black = (0,0,0)
        points = map(lambda x: self.calcScreenPos(x), board.tiles)
        pygame.draw.lines(disp, black, False, list(points), 5)
        size = Point(x=40,y=40)
        for i in board.tiles:
            color = black
            if i in board.hulkTiles:
                color = (76,153,0) # green
            if i in board.endTiles:
                color = (102,0,0) # dark red
            pos = self.calcScreenPos(i)
            pygame.draw.rect(
                disp,
                color,
                (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y)
            )
            font("%i"%i, pos)
        size = Point(x=30,y=30)
        for (player, pc) in (gamestate.players + gamestate.hulks):
            pos = self.calcScreenPos(player.getPos())
            color = Renderer.colors[player.getColor()]
            pygame.draw.ellipse(
                disp,color,
                (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y)
            )
        
