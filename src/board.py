tiles = range(0,56)

def calculate(tileNumber):
    import math
    from collections import namedtuple
    Point = namedtuple('Point', ['x', 'y'])
    return Point(x=tileNumber * math.cos(tileNumber),y=tileNumber * math.sin(tileNumber))

class TilePositionCalculator:
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
        return (tileNumber * math.cos(tileNumber), tileNumber * math.sin(tileNumber))
