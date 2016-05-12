tiles = range(0,56)

from collections import namedtuple
import math

Point=namedtuple('Point',['x','y'])
"""
In a number
Out some coordinates (non scaled, just as a grid)
"""
def calcPosition(tileNumber):
    # thanks: https://math.stackexchange.com/questions/163080/on-a-two-dimensional-grid-is-there-a-formula-i-can-use-to-spiral-coordinates-in
    # second anwser after spending more than 2 hours on the first.
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

"""
Renders a board
"""
class Renderer:
    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.borderpadding = 0.05
        def scale(num):
            return (num*(1-2*self.borderpadding))/math.sqrt(len(tiles))
        self.scale = Point(
            x=scale(screenSize.width),
            y=scale(screenSize.height)
        )

    def render(self, font):
        for i in tiles:
            pos = calcPosition(i+1)
            pos = (
                pos.x*self.scale.x+self.screenSize.width*(0.5-self.borderpadding),
                pos.y*60+self.screenSize.height*(0.5-self.borderpadding))
            font("%i"%i, pos)
