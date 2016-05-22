#!/usr/bin/env python
"""This file starts the game"""

import pygame
from pgu import gui, timer


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

class TestDialog(gui.Dialog):
    def __init__(self):
        title = gui.Label("Some Dialog Box")
        label = gui.Label("Close self window to resume.")
        gui.Dialog.__init__(self, title, label)

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

        #self.setup_menu(container)
        import human_player
        human_player.App(self.menuArea)
        
        container.add(tbl,0,0)
        self.init(container, disp)

    def setup_menu(self):
        tbl = gui.Table(vpadding=5, hpadding=2)
        tbl.tr()

        dlg = TestDialog()

        def dialog_cb():
            dlg.open()

        btn = gui.Button("Modal dialog", height=50)
        btn.connect(gui.CLICK, dialog_cb)
        tbl.td(btn)

        # Add a button for pausing / resuming the game clock
        def pause_cb():
            if (self.engine.clock.paused):
                self.engine.resume()
            else:
                self.engine.pause()

        btn = gui.Button("Pause/resume clock", height=50)
        btn.connect(gui.CLICK, pause_cb)
        tbl.td(btn)

        # Add a slider for adjusting the game clock speed
        tbl2 = gui.Table()

        timeLabel = gui.Label("Clock speed")

        tbl2.tr()
        tbl2.td(timeLabel)

        slider = gui.HSlider(value=23,min=0,max=100,size=20,height=16,width=120)

        def update_speed():
            self.engine.clock.set_speed(slider.value/10.0)

        slider.connect(gui.CHANGE, update_speed)

        tbl2.tr()
        tbl2.td(slider)

        tbl.td(tbl2)

        self.menuArea.add(tbl, 0, 0)

    def open(self, dlg, pos=None):
        # Gray out the game area before showing the popup
        rect = self.gameArea.get_abs_rect()
        dark = pygame.Surface(rect.size).convert_alpha()
        dark.fill((0,0,0,150))
        pygame.display.get_surface().blit(dark, rect)
        # Save whatever has been rendered to the 'game area' so we can
        # render it as a static image while the dialog is open.
        self.gameArea.save_background()
        # Pause the gameplay while the dialog is visible
        running = not(self.engine.clock.paused)
        self.engine.pause()
        gui.Desktop.open(self, dlg, pos)
        while (dlg.is_open()):
            for ev in pygame.event.get():
                self.event(ev)
            rects = self.update()
            if (rects):
                pygame.display.update(rects)
        if (running):
            # Resume gameplay
            self.engine.resume()

    def get_render_area(self):
        return self.gameArea.get_abs_rect()


"""In our main drawing are we don't want to use pgu because
its event driven, so you can't do any movement (since you need
events to move, so you'll get stupid stuff like only movement
on mouse move). The game engine punches a hole in the pgu
interface and keeps updating that hole."""
class GameEngine(object):
    def __init__(self, disp):
        self.disp = disp
        self.app = MainGui(self.disp)
        self.app.engine = self
        self.speed = [1, 2]
        from board import Renderer
        from collections import namedtuple
        Size = namedtuple('Size', ['width', 'height'])
        # construct factory, which gets used to (eventually) create the game manager
        from factory import Factory
        factory = Factory('config.json')
        pcs = factory.makePlayerControllers()
        state = factory.makeState(pcs)
        self.gameManager = factory.makeGameManager(state)
        # create board 
        self.renderBoard = Renderer(Size(
            self.app.gameArea.rect.width,
            self.app.gameArea.rect.height
        )).render # a function

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


    def run(self):
        self.app.update()
        pygame.display.flip()

        self.font = pygame.font.SysFont("", 16)

        self.clock = timer.Clock() #pygame.time.Clock()
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

###
disp = pygame.display.set_mode((1366, 768))
eng = GameEngine(disp)
eng.run()
