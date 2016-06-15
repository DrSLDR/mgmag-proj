#!/usr/bin/env python
"""The purpose of this file is to run the game a great many times in order to
extract more-or-less useful statistics about the game. This file is not intended
to be used as a component of something else and works as a combination of
main.py and engine.py.

The file works in two stages. The first is data harvesting, during which it runs
a game with the specified configuration CYCLES number of times. The data is
stored in JSON-like structures (dictionaries) which contains the game turn
count (which is useful for determining game length) and a sub-object, mapping
players to lists of positions. Thus, a player's performance can be tracked
across games. These structures are then maintained sequentially in the main data
list.

The second stage is data crunching. Based on the command-line flags given to the
program, different statistical functions will be run on the data set. The
functions do not modify the core data set, so several statistical functions can
be run in series.

TODO: separation of powers, win-count tracking, data export/import

"""

import engine, factory, main, argparse, statistics
# Prep the parser
parser = argparse.ArgumentParser(
    description="Runs statistical analysis on Gravitas")
parser.add_argument("-c", "--config", default="config.json",
                    required=True,
                    help="Name of configuration file.\n"+
                    "Checks for \"config.json\" if not given.\n"+
                    "If configuration file is not found or cannot be\n"+
                    "parsed, an exception is thrown.")
parser.add_argument("-n", "--cycles", type=int, default=200,
                    help="Specifies how many games should be run for analysis.")

def run(cycles, fact):
    # Prepare data containers
    data = []
    variances = []
    for i in range(cycles):
        cyc = [-1]*36
        variances.append(cyc)
    
    # Run the loop
    for cycle in range(cycles):
        # Retrieve the important bits
        (engine, manager) = fact.createHeadless()
        
        # Set run parameters
        done = False
        cdata = []
        i = 0
        while not done:
            # Prepare data-gathering
            while manager.copyState().GMState < manager.GMStates['resolve']:
                if engine.update(): # Run the game up to resolution
                    done = True
                    break # Break the loop if someone has already won
            if done:
                break # No more collections
            while manager.copyState().GMState == manager.GMStates['resolve']:
                if engine.update(): # Finish the resolution step
                    done = True
                    break # Game is over, time to collect data
                    
            # Collect data for the turn
            state = manager.copyState()
            rdata = [state.getPlayer(key).ship.getPos() for key in
                     state.players]
            cdata.append(rdata)
            variances[cycle][i] = statistics.variance(rdata)
            i += 1

        # Append most recent data
        data.append(cdata)
        
    # Throw out averages
    varavgs = [-1]*36
    for i in range(36):
        valid = 0
        sum = 0
        for game in variances:
            if game[i] >= 0:
                valid += 1
                sum += game[i]
        if valid > 0:
            varavgs[i] = sum / valid
    print(varavgs)

# Runtime bit
if __name__ == "__main__":
    # Do the parsering
    args = parser.parse_args()
    # Do the other parsering
    margs = main.parser.parse_args(['-c', args.config, '--headless', '-l', '0'])
    # Factorize the factory
    fact = factory.Factory(margs)
    # Launch the run
    run(args.cycles, fact)
