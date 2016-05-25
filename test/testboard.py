import gravitas.model
import gravitas.board
import unittest

class TestBoard(unittest.TestCase):

    def test_calcPosition(self):
        self.assertEqual((0,0),board._calcPosition(1))
        self.assertEqual((1,0),board._calcPosition(2))
        self.assertEqual((1,1),board._calcPosition(3))
        self.assertEqual((0,1),board._calcPosition(4))
        self.assertEqual((0,-1),board._calcPosition(0))
        self.assertEqual((-1,1),board._calcPosition(5))
        self.assertEqual((2,-1),board._calcPosition(10))

if __name__ == '__main__':
    unittest.main()
