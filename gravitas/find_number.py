#!/usr/bin/env python
"""In this file we try to find the number that indicates
with some statistic certainty the how strong a player is

The trick being used is that if only 4 random players play
which are of equal strength because they play randomly,
so they need to win 25% of the time each.

What we want to find is with which number of plays this
becomes almost surely certain.
So if we play a game say 40 times and eveyone pricesely wins
25% of the time, for 30 times, we know that 40 is the good enough,
since 30 is the accepted minimum of statistic
"""
import main
import json
from factory import Factory

acceptedMinimum = 30

currentGameCount = 4 # the amount of games we test
nextChange = 4 # how much to increase currentGameCount next time
changeFactor = 2 # keep on dubbeling untill we found a valid number
playerCount = 4 # if we fall below this number we currentGameCount is the magick number

args = main.parser.parse_args(['-c', 'conf/allrand.json', '--headless', 't'])
factory = Factory(args)
balcount = 0

def isBalanced(gameCount):
    scoreboard = dict((p[0].getName(),0) for p in factory.createState().players)
    for _ in range(0,gameCount):
        score = main.run(factory)
        scoreboard[score[-1][0]] += 1
        if scoreboard[score[-1][0]] > gameCount/playerCount:
            print("imbalanced %s", json.dumps(scoreboard))
            return False
    print("balanced %s", json.dumps(scoreboard))
    return True

for _ in range(0,acceptedMinimum):
    # output the information we need for statistics
    if isBalanced(currentGameCount):
        balcount += 1
    result = main.run(factory)

print("balanced count %i" % balcount)
