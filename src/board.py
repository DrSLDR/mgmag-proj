tiles = range(0,56)

from collections import namedtuple
class PositionCalculator:
    """
    Configures the calulate function
    """
    def __init__(self, size):
        self.size = size
        def unit(value):
            return 2.5-(value/len(tiles))
        def smallerThen(this,value,elsefunction):
            def func(x):
                if x < this:
                    return value
                else:
                    return elsefunction(x)

            return func
        self.scaleFactor = unit
        pass

    """
    In a number
    Out some coordinates
    """
    def calcPosition(self,tileNumber):
        import math
        Point = namedtuple('Point', ['x', 'y'])
        power = self.scaleFactor(tileNumber)
        return Point(
            x=(self.size.width / tileNumber) * math.cos(tileNumber**(1/power)),
            y=(self.size.height / tileNumber) * math.sin(tileNumber**(1/power))
        )
class Renderer:
    def __init__(self, screenSize):
        tmp = PositionCalculator(screenSize)
        self.screenSize = screenSize
        self.calulator = tmp.calcPosition

    def render(self, font):
        for i in tiles:
            pos = self.calulator(i+1)
            pos = (pos[0]+self.screenSize.width/2, pos[1]++self.screenSize.height/2)
            font("%i"%i, pos)
