"""File for the factory class, containing a bunch of init logic (such
as loading of configuration)"""

import pygame
from pgu import gui, timer
import random, json
from model.player import Player
from model.ship import Ship
from model.card import Card, Deck
from gamemanager import State, GameManager
from controller.random import RandomAI_PC, RandomIgnoreEmergency
from controller.human import Human_PC
from controller.neural import Neurotic_PC
from controller.symbolic import SymbolicAI_PC
from engine import GameEngine, callog
from human_player import MainGui, FrameRateThrottler, ScreenRenderer

class Factory():
    """ A factory which can create playerControllers, states and the Gamemanager"""

    def __init__(self, args):
        self.args = args
        #The player type dictionary mapping of known player types to
        #the constructor for their respective player controller. 
        self._controllerTypes = {
            "human": Human_PC,
            "randAI": RandomAI_PC,
            "neuroticAI": Neurotic_PC,
            "symbolic": SymbolicAI_PC,
            "randIgnoreEmergency": RandomIgnoreEmergency
        }
        self.guiContainer = None
        self._configureLogger() # cause you know, need it to operate

    @callog
    def _parseConfig(self, config):
        """Helper function that reads the configuration file"""
        f = open(config, 'r')
        conflist = json.load(f)
        f.close()
        self.log.debug("Got config file contents as: %s", conflist)
        for c in conflist:
            self.log.debug("Handling object %s", c)
            if not c['type'] in self._controllerTypes:
                self.log.error("Unknown agent type %s in %s", c['type'],
                               c['name'])
        return conflist

    @callog
    def _createPlayerController(self, player, config):
        """return list of player controllers, whose properties depend on the
        config file"""
        if config['type'] not in self._controllerTypes:
            self.log.error("No player controller definition exists for %s",
                           config['type'])
            return None

        self.log.debug("Player controller definition exists for type %s",
                        config['type'])
        if self._controllerTypes[config['type']] is None:
            self.log.warning("Player controller type %s is not implemented",
                                config['type'])
            return None
        self.log.debug("Constructing player controller")
        # Bind the arguments
        args = config['arguments']
        # Invoke the constructor
        return self._controllerTypes[config['type']](player, args,
                                                self.guiContainer)
    
    @callog
    def createState(self):
        """create a game state and put the player controllers in there"""
        # create empty state
        state = State()

        config = self._parseConfig(self.args.config)
        # Create the player objects
        availColors = [1,2,3,4]
        for p in config:
            self.log.debug("Handling player %s", p)
            c = random.choice(availColors)
            availColors.remove(c)
            self.log.debug("Selected %i as color", c)
            self.log.debug("Creating player model")
            player = Player(c, p['name'])
            self.log.debug("Creating player controller")
            pc = self._createPlayerController(player, p)
            if pc is not None:
                self.log.info("Adding %s's player tuple to state", p['name'])
                state.addPlayer(player, pc)
            else:
                self.log.error("No player controller created for %s. Skipping.",
                               p['name'])

        # Create NPC ships ("hulks")
        # Angry Marines all up in this
        # See https://1d4chan.org/wiki/Angry_Marines for ship name references
        self.log.info("Adding tile 36 hulk to state")
        state.addHulk("Litany of Litany's Litany", 36)
        if len(config) > 2:
            self.log.info("More than two players. Adding tile 26 hulk to state")
            state.addHulk("Belligerent Engine", 26)

        return state

    @callog
    def _createGameManager(self):
        """Given the game manager configuration, create the game manager"""
        state = self.createState()
        return GameManager(state)

    def _configureLogger(self):
        import logging
        if(self.args.loglevel == 0):
            # Create dummy logger
            logging.basicConfig(level=51)
        else:
            if(self.args.loglevel == 1):
                level = logging.CRITICAL
            elif(self.args.loglevel == 2):
                level = logging.ERROR
            elif(self.args.loglevel == 3):
                level = logging.WARNING
            elif(self.args.loglevel == 4):
                level = logging.INFO
            elif(self.args.loglevel == 5):
                level = logging.DEBUG
            # Configure and prepare logger
            logging.basicConfig(
                filename=self.args.logfile, filemode='w', level=level,
                format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")

        # Declare
        self.log = logging.getLogger(__name__)
        self.log.info("Log initiated")

    @callog
    def createGameManager(self):
        """Create game function. Main function of the class. Sets handles the
        command line arguments, if any, and returns the game manager."""
        # Configuration file
        self.log.info("Attempting to parse configuration file %s",
                      self.args.config)
        # Create and return the game manager
        self.log.info("Starting creation of Game Manager")
        return self._createGameManager()

    @callog
    def createHeadless(self):
        """Create a headless game."""
        gamemanager = self.createGameManager()
        engine = GameEngine()
        engine.updateables.append(gamemanager)
        return (engine, gamemanager)

    @callog
    def createGUIEngine(self):
        """Create a headed game."""
        display = pygame.display.set_mode((1366, 768))
        gui = MainGui(display)
        self.guiContainer = gui.menuArea
        (engine, manager) = self.createHeadless()
        gui.gameManager = manager
        gui.update()
        pygame.display.flip()
        engine.updateables.append(ScreenRenderer(gui))

        throtle = FrameRateThrottler(manager, engine)
        engine.updateables.append(throtle)
        return (engine, manager)

