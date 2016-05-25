"""File for the factory class, containing a bunch of init logic (such
as loading of configuration)"""

import pygame
from pgu import gui, timer
import random, json
from player import Player, Ship
from card import Card, Deck
from gamemanager import State, GameManager
from player_controller import RandomAI_PC, Human_PC

class Factory():
    """ A factory which can create playerControllers, states and the Gamemanager"""

    def __init__(self, args, guiContainer):
        self.args = args
        #The player type enumeration dictionary mapping of known player types to
        #the constructor for their respective player controller. 
        self._PType = {
            "human": Human_PC,
            "randAI": RandomAI_PC
        }
        self.guiContainer = guiContainer

    def _parseConfig(self, config):
        """Helper function that reads the configuration file"""
        f = open(config, 'r')
        conflist = json.load(f)
        f.close()
        for c in conflist:
            if not c['type'] in self._PType:
                print("ERROR: Unknown agent type " + c['type'])
        return conflist

    def _createPlayerController(self, player, config):
        """return list of player controllers, whose properties depend on the config
        file"""
        if self._PType[config['type']] is None:
            print("Non-implemented player controller")
            return None
        else:
            # Bind the arguments
            args = config['arguments']
            # Invoke the constructor
            return self._PType[config['type']](player, args, self.guiContainer)

    def _createState(self, config):
        """create a game state and put the player controllers in there"""
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

    def _createGameManager(self, config):
        """Given the game manager configuration, create the game manager"""
        state = self._createState(config)
        return GameManager(state)

    def createGame(self):
        """Create game function. Main function of the class. Sets handles the
        command line arguments, if any, and returns the game manager."""
        # Prepares the RNG
        random.seed() # wut?! You need to do this in python, appearantly not...
        # see: https://stackoverflow.com/questions/817705/pythons-random-what-happens-if-i-dont-use-seedsomevalue

        # Runs over the arguments
        # Configuration file
        try:
            config = self._parseConfig(self.args.config)
        except Exception:
            print("OHSNAP")
            raise
        
        # Create and return the game manager
        return self._createGameManager(config)
    
