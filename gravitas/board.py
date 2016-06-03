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
        Ship.Color.red: (222,0,0),
        Ship.Color.blue: (0,162,232),
        Ship.Color.yellow: (254,222,1),
        Ship.Color.green: (33,217,0),
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

    def render(self, font, disp, gamestate, human, revealedCards):
        """function that renders the board"""
        import pygame
        # connections between tiles
        black = (0,0,0)
        points = map(lambda x: self.calcScreenPos(x), board.tiles)
        pygame.draw.lines(disp, black, False, list(points), 5)
        # board tiles
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
        # player and hulk ships
        size = Point(x=30,y=30)
        for (player, pc) in (gamestate.players + gamestate.hulks):
            pos = self.calcScreenPos(player.getPos())
            color = Renderer.colors[player.getColor()]
            # draw white bordered circle filled with ship-color
            pygame.draw.ellipse(
                disp, (250,250,250), 
                (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y)
            )
            pygame.draw.ellipse(
                disp,color, 
                (pos.x-size.x/2+1, pos.y-size.y/2+1, size.x-2,size.y-2)
            )
        # round annotation
        pos = Point(x=20,y=20)
        font("Round %i"%(gamestate.round+1), pos)

        def drawCard(card, font, disp, pos, borderColor = (120,120,120)):
            color = (90,90,90) # about the same color as the buttons
            size = Point(x=80, y=60) # size of card
            # draws a grey square filled with with card info
            pygame.draw.rect(disp, borderColor, 
                (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y))
            pygame.draw.rect(disp, color, 
                (pos.x-size.x/2+2, pos.y-size.y/2+2, size.x-4,size.y-2))
            # value
            font("%i"%card.getValue(), Point(x=pos.x-5,y=pos.y-20   ) )
            # short name
            font(card.getName() , Point(x=pos.x-5,y=pos.y-5) )
            #type
            cardType = card.getType()
            if cardType == 0:
                cardTypeStr = ' Normal  '
            elif cardType == 1:
                cardTypeStr = 'Repulsor'
            else: cardTypeStr = ' Tractor  '
            font(cardTypeStr , Point(x=pos.x-20,y=pos.y+10) )

        # gets the first human from the state
        
        if human is not None:
            # display human player's name in color of their ship
            color = Renderer.colors[human["color"]]  
            darkerColor = (2/3*color[0],2/3*color[1],2/3*color[2])
            pos = Point(x=620,y=490)
            size = Point(x=80, y=30) 
            pygame.draw.rect(disp, 
                color, 
                (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y))
            pygame.draw.rect(disp, darkerColor,                
                (pos.x-size.x/2+2, pos.y-size.y/2+2, size.x-4,size.y-2))
            font(human["name"], Point(x=pos.x-20,y=pos.y-5))

            # display their cards
            spacing = 0
            for card in human["hand"]:
                drawCard(card, font, disp, Point(x=720+spacing,y=470))
                spacing += 100

            # draw (lack of) ES 
            size = Point(x=80, y=60) # size of card
            pos = Point(x=720+spacing,y=470)

            if human["canES"]:
                # draws ER-rect with a white border (in same color as human ship)
                pygame.draw.rect(disp, color, (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y))
                pygame.draw.rect(disp, darkerColor, (pos.x-size.x/2+2, pos.y-size.y/2+2, size.x-4,size.y-2))
                font("Emergency" , Point(x=pos.x-28,y=pos.y-10) )
                font("Stop" , Point(x=pos.x-12,y=pos.y+5 ) )
            else:
                # draw empty bordered rect
                pygame.draw.rect(disp, color, (pos.x-size.x/2, pos.y-size.y/2, size.x,size.y))
                pygame.draw.rect(disp, (20,20,20), (pos.x-size.x/2+2, pos.y-size.y/2+2, size.x-4,size.y-2))
                font("ES played" , Point(x=pos.x-28,y=pos.y) )

            # draw revealed cards
            spacing = (len(gamestate.players)-len(revealedCards) )*100
            for card in revealedCards[0]:
                colorNr = revealedCards[1][card.getName()]
                cardBorder = Renderer.colors[colorNr]
                drawCard(card, font, disp, Point(x=100+spacing,y=470),cardBorder)
                spacing += 100







