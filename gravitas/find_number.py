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

currentGameCount = 240 # the amount of games we test
change = 40 # how much to increase currentGameCount next time
playerCount = 2
leeway = 1.1 # allow some deviation

args = main.parser.parse_args(['-c', 'conf/tworand.json', '--headless', 't'])
factory = Factory(args)

def isBalanced(gameCount):
    if not gameCount % playerCount == 0:
        raise ValueError("game count has to be devidable by playercount")
    scoreboard = dict((p[0].getName(),0) for p in factory.createState().players)
    for _ in range(0,gameCount):
        score = main.run(factory)
        scoreboard[score[-1][0]] += 1
        if scoreboard[score[-1][0]] > (gameCount/playerCount) * leeway :
            print("imbalanced %s" % json.dumps(scoreboard))
            return False
    print("balanced %s" % json.dumps(scoreboard))
    return True

while True:
    balcount = 0
    for _ in range(0,acceptedMinimum):
        # output the information we need for statistics
        if not isBalanced(currentGameCount):
            currentGameCount += change
            break
        balcount += 1
    print("count %i, games played %i" % (balcount, currentGameCount-change))
    if balcount == (acceptedMinimum-1):
        break

print("Magick number is %i" % currentGameCount)

