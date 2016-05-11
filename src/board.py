tiles = range(0,56)

from collections import namedtuple
class PositionCalculator:
    """
    Configures the calulate function
    """
    def __init__(self, size):
        self.size = size
        pass

    """
    In a number
    Out some coordinates
    """
    def calcPosition(self,tileNumber):
        import math
        # explenation: https://math.stackexchange.com/questions/163080/on-a-two-dimensional-grid-is-there-a-formula-i-can-use-to-spiral-coordinates-in
        # tileSize = n from explenation
        spiralSize = abs(math.sqrt(tileNumber)) # (m in explenation)
        spirStep = 0 # k in explenation
        if spiralSize % 2 == 1: # is odd
            spirStep = (spiralSize-1)/2
        elif tileNumber >= (spiralSize**2 + spiralSize): # n >= m(m+1)
            spirStep = spiralSize/2
        else:
            spirStep = spiralSize/2-1

        Point = namedtuple('Point', ['x', 'y'])
        factor = 60
        if 2*spirStep *(2*spirStep + 1) < tileNumber <= (2*spirStep + 1) ** 2:
            print("bleh")
            return Point(
                x=(tileNumber-4*spirStep**2-3*spirStep)*factor,
                y=spirStep*factor
            )
        if (2*spirStep + 1)**2 < tileNumber <= 2*(spirStep+1)*(2*spirStep+1):
            print("bluh")
            return Point(
                x=(spirStep+1)*factor,
                y=(4*spirStep**2+5*spirStep+1-tileNumber)*factor
            )
        if 2*(spirStep + 1)*(2*spirStep+1) < tileNumber <= 4*(spirStep+1)**2:
            print("bloh")
            return Point(
                x=(4*spirStep**2+7*spirStep+3-tileNumber)*factor,
                y=(-spirStep-1)*factor
            )
        if 4*(spirStep + 1)**2 < tileNumber <= 2*(spirStep+1)*(2*spirStep+3):
            print("blah")
            return Point(
                x=(-spirStep-1)*factor,
                y=(tileNumber-4*spirStep**2-9*spirStep-5)*factor,
            )

        return Point(
            x=0,
            y=0
        )
class Renderer:
    def __init__(self, screenSize):
        tmp = PositionCalculator(screenSize)
        self.screenSize = screenSize
        self.calulator = tmp.calcPosition

    def render(self, font):
        for i in tiles:
            pos = self.calulator(i+1)
            pos = (pos[0]+self.screenSize.width/2, pos[1]+self.screenSize.height/2)
            font("%i"%i, pos)
