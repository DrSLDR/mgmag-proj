from gravitas.model import player
import unittest

class TestPlayer(unittest.TestCase):

    def distanceToFinish(self):
        player = Player(None,None)
        self.assertEqual(player.distanceToFinish(), 54)


if __name__ == '__main__':
    unittest.main()
