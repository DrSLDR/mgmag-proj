import pygame
from pgu import gui, timer
import random, json
from player import Player, Ship
from card import Card, Deck
from gamemanager import State, GameManager
from pc import RandomAI_PC, Human_PC
"""Class that creates a factory, which can in turn create other objects;
 playerControllers, states and the Gamemanager"""

class Factory():

    def __init__(self, args):
        self.args = args
        #The player type enumeration dictionary mapping of known player types to
        #the constructor for their respective player controller. 
        self._PType = {
            "human": Human_PC,
            "randAI": RandomAI_PC
        }

    """Helper function that reads the configuration file"""
    def _parseConfig(self, config):
        f = open(config, 'r')
        conflist = json.load(f)
        f.close()
        for c in conflist:
            if not c['type'] in self._PType:
                print("ERROR: Unknown agent type " + c['type'])
        return conflist

    """return list of player controllers, whose properties depend on the config
    file"""
    def _createPlayerController(self, player, config):
        if self._PType[config['type']] is None:
            print("Non-implemented player controller")
            return None
        else:
            # Bind the arguments
            args = config['arguments']
            # Invoke the constructor
            return self._PType[config['type']](player, args)

    """create a game state and put the player controllers in there"""
    def _createState(self, config):
        # create empty state
        state = State()

        # Create the player objects
        availColors = [1,2,3,4]
        for p in config:
            c = random.choice(availColors)
            availColors.remove(c)
            player = Player(c, p['name'])
            pc = self._createPlayerController(player, p)
            state.addPlayer((player, pc))

        # Create NPC ships ("hulks")
        state.addHulk(36)
        if len(config) > 2:
            state.addHulk(26)

        return state

    """Given the game manager configuration, create the game manager"""
    def _createGameManager(self, config):
        state = self._createState(config)
        return GameManager(state)

    """Create game function. Main function of the class. Sets handles the
    command line arguments, if any, and returns the game manager."""
    def createGame(self):
        # Prepares the RNG
        random.seed()

        # Runs over the arguments
        # Configuration file
        try:
            config = self._parseConfig(self.args.config)
        except Exception:
            print("OHSNAP")
            raise
        
        # Create and return the game manager
        return self._createGameManager(config)
