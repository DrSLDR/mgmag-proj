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

Note that the algorithm is not optimized: each statistical function is given the
full dataset to work over alone. Consecutive by-line operations could be
implemented but aren't because time constraint.

TODO: win-count tracking, position mean and standard variation: global, per
      turn, per player, per player per turn

"""

import engine, factory, main, argparse, statistics, json

def run(cycles, fact):
    """Runs the game to gather data.

    Takes the number of cycles (games) to run and the game factory as
    arguments.

    Returns the data list.

    """

    # Prepare the master data list
    data = []
    
    # Run the loop
    for cycle in range(cycles):
        # Retrieve the important bits
        (engine, manager) = fact.createHeadless()
        
        # Prepare game dataset
        state = manager.copyState()
        gameData = {'turn' : 0, 'players' : {}}
        for key in state.players:
            gameData['players'][key] = []

        # Do the game
        done = False
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
            for key in state.players:
                gameData['players'][key].append(
                    state.getPlayer(key).ship.getPos())
            if not done:
                gameData['turn'] += 1

        # Append most recent data
        data.append(gameData)

    return data

def process(data, args):
    """Main switchboard between statistics functions.

    Takes the main data and the parser arguments.

    Returns nothing. Sub-functions may print.

    """
    argsdict = vars(args)
    glob = globals().copy()
    glob.update(locals())
    for key in argsdict:
        if "stats_" in key:
            if args.all or argsdict[key]:
                method = glob.get(key)
                method(data)
                
def stats_winCount(data):
    """Counts and prints the per-player win count in the dataset."""

    # Prepare the result data
    result = {}
    for key in data[0]['players']:
        result[key] = 0

    # Crunch
    for game in data:
        winner = None
        dist = 0
        for key in game['players']:
            if game['players'][key][-1] > dist:
                dist = game['players'][key][-1]
                winner = key
        result[winner] += 1

    # Print
    print("Win counts:")
    print(str(result) + "\n")

# Runtime bit
if __name__ == "__main__":
    # Prep the parser
    parser = argparse.ArgumentParser(
        description="Runs statistical analysis on Gravitas")
    parser.add_argument("-n", "--cycles", type=int, default=200,
                        help="""Specifies how many games should be run for
                        analysis. Defaults to 200 if not specified. Ignored if a
                        data file (--data) is provided.""")

    iogroup = parser.add_argument_group("I/O", description="""Options governing
    the input and output of data from the statistics script. Either --data or
    --config must be given.""")
    iomutex = iogroup.add_mutually_exclusive_group(required=True)
    iomutex.add_argument("-c", "--config", help="""Name of configuration
                         file. If configuration file is not found or cannot be
                         parsed, an exception is thrown.""")
    iomutex.add_argument("-d", "--data", help="""Name of the data file. Allows
                         re-using previously dumped data. If the data file is
                         not found or cannot be parsed, an exception is
                         thrown.""")
    iogroup.add_argument("--dump", help="""Name of the data file in which this
                         run's data should be dumped. Ignored if a data file
                         (--data) is provided.""")

    statsgroup = parser.add_argument_group("Statistics", description="""Switches
    to turn statistical operations on.""")
    statsgroup.add_argument("--all", action="store_true", help="""The kitchen
                            sink. Runs every implemented statistical
                            function.""")
    statsgroup.add_argument("--win-count", action="store_true",
                            dest="stats_winCount", help="""Counts the number of
                            wins for each player.""")

    # Do the parsering
    args = parser.parse_args()

    # Figure out if we are doing a run or an import
    if args.data is not None:
        # Looks an awful lot like an import
        datafile = open(args.data, 'r')
        data = json.load(datafile)
        datafile.close()

    elif args.config is not None:
        # Looks like a run
        # Do the other parsering
        margs = main.parser.parse_args(['-c', args.config, '--headless', '-l',
                                        '0'])
        # Factorize the factory
        fact = factory.Factory(margs)
        # Launch the run
        data = run(args.cycles, fact)
        # Dump, if that was necessary
        if args.dump is not None:
            dumpfile = open(args.dump, 'w')
            json.dump(data, dumpfile)
            dumpfile.close()
        
    # Process the recieved data
    process(data, args)
