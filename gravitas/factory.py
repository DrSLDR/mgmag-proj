"""File for the factory class, containing a bunch of init logic (such
as loading of configuration)"""

import pygame
from pgu import gui, timer
import random, json
from model.player import Player
from model.ship import Ship
from model.card import Card, Deck
from gamemanager import State, GameManager
from controller.random import RandomAI_PC
from controller.human import Human_PC
from engine import GameEngine
from human_player import MainGui, FrameRateThrottler, ScreenRenderer

class Factory():
    """ A factory which can create playerControllers, states and the Gamemanager"""

    def __init__(self, args):
        self.args = args
        #The player type dictionary mapping of known player types to
        #the constructor for their respective player controller. 
        self._controllerTypes = {
            "human": Human_PC,
            "randAI": RandomAI_PC
        }
        self.guiContainer = None

    def _parseConfig(self, config):
        """Helper function that reads the configuration file"""
        self.log.debug("Inside %s", self._parseConfig.__name__)
        f = open(config, 'r')
        conflist = json.load(f)
        f.close()
        self.log.debug("Got config file contents as: %s", conflist)
        for c in conflist:
            self.log.debug("Handling object %s", c)
            if not c['type'] in self._controllerTypes:
                self.log.error("Unknown agent type %s in %s", c['type'],
                               c['name'])
        self.log.debug("%s returning", self._parseConfig.__name__)
        return conflist

    def _createPlayerController(self, player, config):
        """return list of player controllers, whose properties depend on the
        config file"""
        self.log.debug("Inside %s", self._createPlayerController.__name__)
        if config['type'] not in self._controllerTypes:
            self.log.error("No player controller definition exists for %s",
                           config['type'])
            self.log.debug("%s returning",
                           self._createPlayerController.__name__)
            return None

        self.log.debug("Player controller definition exists for type %s",
                        config['type'])
        if self._controllerTypes[config['type']] is None:
            self.log.warning("Player controller type %s is not implemented",
                                config['type'])
            self.log.debug("%s returning",
                            self._createPlayerController.__name__)
            return None
        self.log.debug("Constructing player controller")
        # Bind the arguments
        args = config['arguments']
        # Invoke the constructor
        self.log.debug("%s returning",
                        self._createPlayerController.__name__)
        return self._controllerTypes[config['type']](player, args,
                                                self.guiContainer)

    def _createState(self, config):
        """create a game state and put the player controllers in there"""
        self.log.debug("Inside %s", self._createState.__name__)
        # create empty state
        state = State()

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
                state.addPlayer((player, pc))
            else:
                self.log.error("No player controller created for %s. Skipping.",
                               p['name'])

        # Create NPC ships ("hulks")
        self.log.info("Adding tile 36 hulk to state")
        state.addHulk(36)
        if len(config) > 2:
            self.log.info("More than two players. Adding tile 26 hulk to state")
            state.addHulk(26)

        self.log.debug("%s returning", self._createState.__name__)
        return state

    def _createGameManager(self, config):
        """Given the game manager configuration, create the game manager"""
        self.log.debug("Inside %s", self._createGameManager.__name__)
        state = self._createState(config)
        self.log.debug("%s returning", self._createGameManager.__name__)
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


    def createGameManager(self):
        """Create game function. Main function of the class. Sets handles the
        command line arguments, if any, and returns the game manager."""
        self._configureLogger()
        # Configuration file
        self.log.info("Attempting to parse configuration file %s",
                      self.args.config)
        try:
            config = self._parseConfig(self.args.config)
        except Exception as e:
            self.log.critical("Failed to parse config file!")
            self.log.critical(e)
            raise e
        
        # Create and return the game manager
        self.log.info("Starting creation of Game Manager")
        gm = self._createGameManager(config)
        self.log.debug("%s returning", self.createGameManager.__name__)
        return gm

    def createHeadless(self):
        gamemanager = self.createGameManager()
        engine = GameEngine()
        engine.updateables.append(gamemanager)
        return (engine, gamemanager)

    def createGUIEngine(self):
        display = pygame.display.set_mode((1366, 768))
        self.guiContainer = MainGui(display)
        (engine, manager) = self.createHeadless()
        self.guiContainer.gameManager = manager
        self.guiContainer.update()
        pygame.display.flip()
        engine.updateables.append(ScreenRenderer(self.guiContainer))

        throthle = FrameRateThrottler(engine, manager)
        return engine

