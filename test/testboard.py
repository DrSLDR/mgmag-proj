from gravitas import board
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        calulator = board.PositionCalculator()
        self.assertEqual((1,0),calulator.calcPosition(1))
        self.assertEqual((1,-1),calulator.calcPosition(2))
        self.assertEqual((0,-1),calulator.calcPosition(3))
        self.assertEqual((-1,-1),calulator.calcPosition(4))
        self.assertEqual((0,0),calulator.calcPosition(0))

if __name__ == '__main__':
    unittest.main()
