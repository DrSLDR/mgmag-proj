#!/usr/bin/env python
"""This file starts the game, it also contains the engine (ticking
at a certain pase) and it starts everything else"""

import pygame, argparse
from pgu import gui, timer
from factory import Factory
from board import Renderer
from collections import namedtuple
from strings import Logo
import logging

class DrawingArea(gui.Widget):
    def __init__(self, width, height):
        gui.Widget.__init__(self, width=width, height=height)
        self.imageBuffer = pygame.Surface((width, height))
    def paint(self, surface):
        # Paint whatever has been captured in the buffer
        surface.blit(self.imageBuffer, (0, 0))
    # Call self function to take a snapshot of whatever has been rendered
    # onto the display over self widget.
    def save_background(self):
        display = pygame.displaylay.get_surface()
        self.imageBuffer.blit(display, self.get_abs_rect())

class MainGui(gui.Desktop):
    """It describes all the buttons and stuff like that. This is
    where pgu comes in,"""
    gameAreaHeight = 500
    gameArea = None
    menuArea = None
    # The game engine
    engine = None

    def __init__(self, display):
        gui.Desktop.__init__(self)
        container = gui.Container()
        # Setup the 'game' area where the action takes place
        self.gameArea = DrawingArea(display.get_width(),
                                    self.gameAreaHeight)
        # Setup the gui area
        self.menuArea = gui.Container(width = display.get_width(),
            height=display.get_height()-self.gameAreaHeight)
        tabel = gui.Table(height=display.get_height())
        tabel.tr()
        tabel.td(self.gameArea)
        tabel.tr()
        tabel.td(self.menuArea)
        container.add(tabel,0,0)
        self.init(container, display)

    def get_render_area(self):
        return self.gameArea.get_abs_rect()
    def getHumanPlayerGuiContainer(self):
        return self.menuArea

class GameEngine(object):
    """In our main drawing are we don't want to use pgu because
    its event driven, so you can't do any movement (since you need
    events to move, so you'll get stupid stuff like only movement
    on mouse move). The game engine punches a hole in the pgu
    interface and keeps updating that hole."""
    def __init__(self, disp, args):
        self.disp = disp
        self.app = MainGui(self.disp)
        self.humanPlayerGuiContainer = self.app.getHumanPlayerGuiContainer()
        self.factory = Factory(args,self.humanPlayerGuiContainer)
        self._deltaT = 0.0
        self._prevTime = 0.0

    def init(self):
        """Initializes the game"""
        # Call the factory
        self.gameManager = self.factory.createGame()
        # Get logger
        self.log = logging.getLogger("GameEngine")
        self.log.debug("Inside %s", self.init.__name__)
        # create board
        self.log.debug("Creating game board")
        Size = namedtuple('Size', ['width', 'height'])
        self.renderBoard = Renderer(Size(
            self.app.gameArea.rect.width,
            self.app.gameArea.rect.height
        )).render # a function
        self.app.update()
        pygame.display.flip()
        self.log.debug("Creating font")
        self.font = pygame.font.SysFont("", 16)
        self.log.debug("Creating game clock")
        self.clock = timer.Clock() #pygame.time.Clock()
        self.log.debug("%s returning", self.init.__name__)

    def update(self):
        """updates the game state / execute the game logic"""
        self.log.debug("Inside %s", self.update.__name__)
        self.gameManager.update(self._deltaT)

    def render(self, destination, rect):
        """shows to a player what's going on"""
        backgroundColor = 0, 0, 255 # which is blue
        destination.fill(backgroundColor)
        def font(text, position, color=(255,255,255)):
            tmp = self.font.render(text, True, color)
            destination.blit(tmp, position)
        self.renderBoard(font, disp, self.gameManager.copyState(), 
            self.gameManager.getHuman(), # to draw the hand of the human user
            self.gameManager.getPlayedCards()) # to draw the revealed cards
        return (rect,)

    def run(self):
        """blocking call for the game"""
        self.init()
        self.log.debug("Inside %s", self.run.__name__)
        self.log.info("Entering game loop")
        while True:
            # Process events
            self.log.debug("Handling event queue")
            for ev in pygame.event.get():
                self.log.debug("Handling event %s", ev)
                if (ev.type == pygame.QUIT or 
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    self.log.info("Caught exit action. Quitting.")
                    logging.shutdown()
                    return # cheated out that done variable
                # Pass the event off to pgu
                self.app.event(ev)
            # update logic
            self.update()
            # Render the game
            self.log.debug("Rendering game")
            rect = self.app.get_render_area()
            updates = []
            self.disp.set_clip(rect)
            temp = self.render(self.disp, rect)
            if (temp):
                updates += temp
            self.disp.set_clip()
            # Cap it at 30fps
            self.log.debug("Waiting for 30fps tick")
            currTime = self.clock.get_time()
            self._deltaT = currTime - self._prevTime
            self._prevTime = currTime
            self.clock.tick(30)
            # Give pgu a chance to update the display
            temp = self.app.update()
            if (temp):
                updates += temp
            pygame.display.update(updates)
            pygame.time.wait(10)

# Runtime script
# Prep the parser
parser = argparse.ArgumentParser(
    description="Launches the Gravitas game",
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-c", "--config", default="config.json", 
                    help="Name of configuration file.\n"+
                    "Checks for \"config.json\" if not given.\n"+
                    "If configuration file is not found or cannot be\n"+
                    "parsed, an exception is thrown.")
parser.add_argument("-l", "--log-level", type=int, dest="loglevel",
                    choices=range(6), default=0,
                    help="Desired log level. The levels are:\n"+
                    "1 : CRITICAL - Exceptions and crashes\n"+
                    "2 : ERROR    - Serious, recoverable problems\n"+
                    "3 : WARNING  - Issues or unexpected events\n"+
                    "4 : INFO     - Information on program activity\n"+
                    "5 : DEBUG    - Verbose internal output\n"+
                    "Logging is disabled by default.")
parser.add_argument("-f", "--log-file", default="gravitas.log",
                    dest="logfile",
                    help="Name of the log file.\n"+
                    "Defaults to \"gravitas.log\" if not given.\n"+
                    "Log level must be set for this argument to have\n"+
                    "effect. Also note that existing logfile will be\n"+
                    "truncated without asking.")
# Do the parsering
args = parser.parse_args()
# Do everything else
disp = pygame.display.set_mode((1366, 768))
eng = GameEngine(disp, args)
eng.run()
