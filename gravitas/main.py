#!/usr/bin/env python
"""This file starts the game, it also contains the engine (ticking
at a certain pase) and it starts everything else"""

import pygame, argparse
from pgu import gui, timer
from factory import Factory
from board import Renderer
from collections import namedtuple
from strings import Logo

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
        self.menuArea = gui.Container(
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
        self.app.engine = self  
        self.factory = Factory(args,self.humanPlayerGuiContainer,self.app)

    def init(self):
        """Initializes the game"""
        # Call the factory
        self.gameManager = self.factory.createGame()
        # create board 
        Size = namedtuple('Size', ['width', 'height'])
        self.renderBoard = Renderer(Size(
            self.app.gameArea.rect.width,
            self.app.gameArea.rect.height
        )).render # a function
        self.app.update()
        pygame.display.flip()
        self.font = pygame.font.SysFont("", 16)
        self.clock = timer.Clock() #pygame.time.Clock()

    def update(self):
        """updates the game state / execute the game logic"""
        self.gameManager.update()

    def render(self, destination, rect):
        """shows to a player what's going on"""
        backgroundColor = 0, 0, 255 # which is blue
        destination.fill(backgroundColor)
        import math
        def font(text, position, color=(255,255,255)):
            tmp = self.font.render(text, True, color)
            destination.blit(tmp, position)
        self.renderBoard(font, disp, self.gameManager.copyState())
        return (rect,)

    def run(self):
        """blocking call for the game"""
        self.init()
        while True:
            # Process events
            for ev in pygame.event.get():
                if (ev.type == pygame.QUIT or 
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    return # cheated out that done variable
                # Pass the event off to pgu
                self.app.event(ev)
            # update logic
            self.update()
            # Render the game
            rect = self.app.get_render_area()
            updates = []
            self.disp.set_clip(rect)
            temp = self.render(self.disp, rect)
            if (temp):
                updates += temp
            self.disp.set_clip()
            # Cap it at 30fps
            self.clock.tick(30)
            # Give pgu a chance to update the display
            temp = self.app.update()
            if (temp):
                updates += temp
            pygame.display.update(updates)
            pygame.time.wait(10)

# Runtime script
# Prep the parser
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default="config.json", help="Name of "+
                    "configuration file")
# Do the parsering
args = parser.parse_args()
# Do everything else
disp = pygame.display.set_mode((1366, 768))
eng = GameEngine(disp, args)
eng.run()
