#!/usr/bin/env python
"""This file starts the game by creating a GUI with pygame"""

import argparse

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
                    choices=range(6), default=5,
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
from factory import Factory
factory = Factory(args)
factory.createGUIEngine().run()
