tiles = range(0,56)

from collections import namedtuple
class PositionCalculator:
    """
    Configures the calulate function
    """
    def __init__(self):
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
        spirStep = spiralSize/2-1 # k in explenation
        print("spirsize %f" % spiralSize)
        if int(spiralSize) % 2 == 1: # is odd
            spirStep = (spiralSize-1)/2
        elif tileNumber >= (spiralSize**2 + spiralSize): # n >= m(m+1)
            spirStep = spiralSize/2
        print("spirStep %f" % spirStep)

        Point = namedtuple('Point', ['x', 'y'])
        if 2*spirStep *(2*spirStep + 1) < tileNumber <= (2*spirStep + 1) ** 2:
            print("bleh n=%f k=%f"%(tileNumber,spirStep))
            return Point(
                x=(tileNumber-4*spirStep**2-3*spirStep),
                y=spirStep
            )
        if (2*spirStep + 1)**2 < tileNumber <= 2*(spirStep+1)*(2*spirStep+1):
            print("bluh n=%f k=%f"%(tileNumber,spirStep))
            return Point(
                x=(spirStep+1),
                y=(4*spirStep**2+5*spirStep+1-tileNumber)
            )
        if 2*(spirStep + 1)*(2*spirStep+1) < tileNumber <= 4*(spirStep+1)**2:
            print("bloh n=%f k=%f"%(tileNumber,spirStep))
            return Point(
                x=(4*spirStep**2+7*spirStep+3-tileNumber),
                y=(-spirStep-1)
            )
        if 4*(spirStep + 1)**2 < tileNumber <= 2*(spirStep+1)*(2*spirStep+3):
            print("blah n=%f k=%f"%(tileNumber,spirStep))
            return Point(
                x=(-spirStep-1),
                y=(tileNumber-4*spirStep**2-9*spirStep-5),
            )
        # Programs perform best with a gun pointed at there head.
        # but the math checks out, so no worries.
        raise Exception("The math does not check out")
class Renderer:
    def __init__(self, screenSize):
        tmp = PositionCalculator(screenSize)
        self.screenSize = screenSize
        self.calulator = tmp.calcPosition

    def render(self, font):
        for i in tiles:
            pos = self.calulator(i+1)
            pos = (pos.x*60+self.screenSize.width/2, pos.y*60+self.screenSize.height/2)
            font("%i"%i, pos)
