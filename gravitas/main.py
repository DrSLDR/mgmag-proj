#!/usr/bin/env python
"""This file starts the game"""

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
    def paint(self, surf):
        # Paint whatever has been captured in the buffer
        surf.blit(self.imageBuffer, (0, 0))
    # Call self function to take a snapshot of whatever has been rendered
    # onto the display over self widget.
    def save_background(self):
        disp = pygame.display.get_surface()
        self.imageBuffer.blit(disp, self.get_abs_rect())

"""It describes all the buttons and stuff like that. This is
where pgu comes in,"""
class MainGui(gui.Desktop):
    gameAreaHeight = 500
    gameArea = None
    menuArea = None
    # The game engine
    engine = None

    def __init__(self, disp):
        gui.Desktop.__init__(self)
        container = gui.Container()
        # Setup the 'game' area where the action takes place
        self.gameArea = DrawingArea(disp.get_width(),
                                    self.gameAreaHeight)
        # Setup the gui area
        self.menuArea = gui.Container(
            height=disp.get_height()-self.gameAreaHeight)
        tbl = gui.Table(height=disp.get_height())
        tbl.tr()
        tbl.td(self.gameArea)
        tbl.tr()
        tbl.td(self.menuArea)
        import human_player
        human_player.App(self.menuArea)
        container.add(tbl,0,0)
        self.init(container, disp)
    def get_render_area(self):
        return self.gameArea.get_abs_rect()


"""In our main drawing are we don't want to use pgu because
its event driven, so you can't do any movement (since you need
events to move, so you'll get stupid stuff like only movement
on mouse move). The game engine punches a hole in the pgu
interface and keeps updating that hole."""
class GameEngine(object):
    def __init__(self, disp, args):
        self.disp = disp
        self.app = MainGui(self.disp)
        self.app.engine = self  
        self.logo = pygame.transform.scale(pygame.image.load(Logo.game),
                                           (200,200)) 
        self.ballrect = self.logo.get_rect()
        self.speed = [1, 2]
        self.factory = Factory(args)

    # Pause the game clock
    def pause(self):
        self.clock.pause()

    # Resume the game clock
    def resume(self):
        self.clock.resume()

    def render(self, dest, rect):
        size = width, height = rect.width, rect.height
        backgroundColor = 0, 0, 255 # which is blue
        dest.fill(backgroundColor)
        import math
        def font(text, position, color=(255,255,255)):
            tmp = self.font.render(text, True, color)
            dest.blit(tmp, position)
        self.gameManager.update()
        self.renderBoard(font, disp)
        return (rect,)

    """Initializes the game"""
    def init(self):
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

    def run(self):
        self.init()
        done = False
        while not done:
            # Process events
            for ev in pygame.event.get():
                if (ev.type == pygame.QUIT or 
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    done = True
                else:
                    # Pass the event off to pgu
                    self.app.event(ev)
            # Render the game
            rect = self.app.get_render_area()
            updates = []
            self.disp.set_clip(rect)
            lst = self.render(self.disp, rect)
            if (lst):
                updates += lst
            self.disp.set_clip()

            # Cap it at 30fps
            self.clock.tick(30)

            # Give pgu a chance to update the display
            lst = self.app.update()
            if (lst):
                updates += lst
            pygame.display.update(updates)
            pygame.time.wait(10)

################################################################################
##### RUNTIME SCRIPT ###########################################################

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
