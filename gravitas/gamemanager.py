"""Module containing the game manager class"""
from player import Player, Ship
from card import Card, Deck
import random

"""Game manager class. Home to all the game's logic."""
class GameManager:

    """Nested class enumerating recognized player types"""
    class PType:
        human = 0
        randAI = 1
    
    """Constructs the game manager. Takes a file pointer to a list of player
    configurations, creates the player and ship objects, hands over control of
    these to the player controllers, then starts the game loop."""
    def __init__(self, config):
        # Bookkeeping
        random.seed()
        self._turn = 0
        self._round = 0
        self._players = []
        self._deck = Deck()

        # Create the player objects
        availColors = [1,2,3,4]
        for p in self._parseConfig(config):
            c = random.choice(availColors)
            availColors.remove(c)
            player = Player(c, p[1])
            self._players.append(player)
            #TODO create and hand over player to player controller

        # Create NPC ships ("hulks")
        self._hulks = [Ship(pos=38)]
        if len(self._players) > 2:
            self._hulks.append(Ship(pos=28))

    """Helper function that reads the configuration file"""
    def _parseConfig(self, config):
        f = open(config, 'r')
        conflist = []
        for l in f:
            l = l.split()
            ptype = eval("GameManager.PType." + l[0])
            conflist.append((ptype, l[1]))
        f.close()
        return conflist

    """Sorts the players based on distance to the warp gate. If two or more
    players are in the singularity, their order is randomized."""
    def sortPlayers(self):
        # Pull all players in the singularity into a separate list
        inS = []
        for p in self._players:
            if p.getPos() == 0:
                inS.append(p)
                self._players.remove(p)

        # Shuffle the players in the singularity
        random.shuffle(inS)

        # Sort the remaining players
        self._players = sorted(self._players, key=lambda p: p.getDistanceToWG())

        # Concatenate
        self._players = self._players + inS

    """Starts the round; deals cards, prompts for selections, and starts the
    round loop"""
    def startRound(self):
        # Sort the players
        self.sortPlayers()

        # Reset all players Emergency Stop
        for p in self._players:
            p.resetES()

        # Prepare the field and start drawing
        field = self._deck.createCardField(len(self._players))
        for i in range(3):
            for p in self._players:
                #TODO prompt the players to draw a card
                # selection = p.promptForChoice(self._deck.percieveCardField())
                # self._deck.takeFromField(selection)
                field = self._deck.getField()
                print("Selection round " + str(i+1) + " for player " +
                      p.getName()) 
                #TODO either wait for the render loop to catch up or call it

    """Turn resolution. Given a list of cards, will sort and resolve plays"""
    def resolve(self, plays):
        #TODO: Things
        return True
