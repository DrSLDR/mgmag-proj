#!/usr/bin/env python
"""This file starts a game"""

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
parser.add_argument("--headless", action="store_true",
                    help="Run without a GUI, useful for statistical analyses")


# executing the script like this allows for injection of a factory
# in case you want to have many games that are configured in the same way
def run(factory):
    (engine, manager) = factory.createHeadless() if factory.args.headless else factory.createGUIEngine()
    engine.run()
    return [(p[0].getName(), p[0].getPos()) for p in manager.copyState().players]

# only execute this if we want to execute this script explicitly
# this is handy for using this code base as a library (which statistical
# analyses does)
if __name__ == "__main__":
    # Do the parsering
    args = parser.parse_args()
    from factory import Factory
    factory = Factory(args)
    # output the information we need for statistics
    import json
    print(json.dumps(run(factory)))
    
