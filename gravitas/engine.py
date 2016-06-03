#!/usr/bin/env python
"""This file starts the game, it also contains the engine (ticking
at a certain pase) and it starts everything else"""

import pygame, argparse
from pgu import gui, timer
from collections import namedtuple
from strings import Logo
import logging

class GameEngine(object):
    """In our main drawing are we don't want to use pgu because
    its event driven, so you can't do any movement (since you need
    events to move, so you'll get stupid stuff like only movement
    on mouse move). The game engine punches a hole in the pgu
    interface and keeps updating that hole."""
    def __init__(self):
        self.updateables = []
        self.framerateThrottle = 0 # 0 for no throttle

        # Get logger
        self.log = logging.getLogger("GameEngine")

        self.log.debug("Creating game clock")
        self.clock = timer.Clock() #pygame.time.Clock()
        self.log.debug("%s returning", self.__init__.__name__)

    def update(self):
        """updates the game state / execute the game logic"""
        self.log.debug("Inside %s", self.update.__name__)
        for updatable in self.updateables:
            self.log.debug("updating %s", type(updatable).__name__)
            if updatable.update():
                return True # winner
        return False

    def run(self):
        """blocking call for the game"""
        self.log.debug("Inside %s", self.run.__name__)
        self.log.info("Entering game loop")
        while True:
            # update logic
            if self.update():
                return
            self.clock.tick(self.framerateThrottle)
