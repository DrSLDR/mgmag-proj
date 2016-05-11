tiles = range(0,56)

from collections import namedtuple

"""
In a number
Out some coordinates
"""
def calcPosition(tileNumber):
    import math
    # thanks: https://math.stackexchange.com/questions/163080/on-a-two-dimensional-grid-is-there-a-formula-i-can-use-to-spiral-coordinates-in
    # second anwser after spending more than 2 hours on the first.
    k=math.ceil((math.sqrt(tileNumber)-1)/2)
    t=2*k+1
    m=t**2 
    t=t-1

    Point=namedtuple('Point',['x','y'])
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

    def render(self, font):
        for i in tiles:
            pos = calcPosition(i+1)
            pos = (pos.x*60+self.screenSize.width/2, pos.y*60+self.screenSize.height/2)
            font("%i"%i, pos)
