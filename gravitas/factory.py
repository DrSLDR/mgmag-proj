import pygame
from pgu import gui, timer
import random, json
from player import Player, Ship
from card import Card, Deck
from gamemanager import State, GameManager

"""Class that creates a factory, which can in turn create other objects;
 playerControllers, states and the Gamemanager"""

class Factory():
    
    """Initialise factory"""
    def __init__(self, configfile):
        # get configuration
        self._initPType()
        self._config = self._parseConfig(configfile)

    """Initializes the player type enumeration dictionary mapping of known
    player types to the constructor for their respective player controller."""
    def _initPType(self):
        self.__PType = {
            "human": None,
            "randAI": None
        }

    """Helper function that reads the configuration file"""
    def _parseConfig(self, config):
        f = open(config, 'r')
        conflist = json.load(f)
        f.close()
        for c in conflist:
            if not c['type'] in self.__PType:
                print("ERROR: Unknown agent type " + c['type'])
                exit(1)
        return conflist

    """return list of player controllers, whose properties depend on the config
    file"""
    def makePlayerControllers(self):
        return None

    """create a game state and put the player controllers in there"""
    def makeState(self, playerControllers):
        # create empty state
        state = State()

        # Create the player objects
        availColors = [1,2,3,4]
        for p in self._config:
            c = random.choice(availColors)
            availColors.remove(c)
            player = Player(c, p['name'])
            state.addPlayer(player)
            #TODO create and hand over player to player controller

        # Create NPC ships ("hulks")
        state.addHulk(36)
        if len(self._config) > 2:
            state.addHulk(26)

        return state

    """Make game manager and give it a current game state"""
    def makeGameManager(self, state):
        gm = GameManager(state)
        return gm
