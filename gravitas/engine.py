#!/usr/bin/env python
"""Contains the engine that keeps updating everything"""

import pygame, argparse
from pgu import gui, timer
from collections import namedtuple
from strings import Logo
from functools import wraps
import logging

class GameEngine(object):
    """Keeps up calling update on some updatables until one of the updatables
    returns some truth (so not none or false)
    also allows throttling of game update speed with framerateThrottle
    """
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
            # by default a python method returns none, which is false
            # but if a method returns truth, we know the game is over
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

def callog(f):
    """Wraps a function to log called arguments and returned data"""
    @wraps(f)
    def wrapper(ref, *args, **kwargs):
        ref.log.debug("%s called with arguments %s, %s", f.__name__, args, kwargs)
        ret = f(ref, *args, **kwargs)
        ref.log.debug("%s returning %s", f.__name__, ret)
        return ret
    return wrapper
