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
# how many times does "balanced" need to come out before we accept it as
# "ballenced"
acceptedMinimum = 30 

currentGameCount = 172 # the amount of games we test
change = 4 # how much to increase currentGameCount next time
leeway = 0.05 # fraction of deviation allowed

args = main.parser.parse_args(['-c', 'conf/tworand.json', '--headless', 't', '-l', '0'])
factory = Factory(args)

playerCount = len(factory.createState().players)

def isBalanced(gameCount):
    if not gameCount % playerCount == 0:
        raise ValueError("game count %i has to be devidable by playercount %i" % (gameCount, playerCount))
    scoreboard = dict((p[0].getName(),0) for p in factory.createState().players)
    avgDistance = 0
    for _ in range(0,gameCount):
        scores = main.run(factory)
        for score in scores:
            scoreboard[score[0]] += score[1]/gameCount
            avgDistance += (score[1]/playerCount)/gameCount

    for value in scoreboard.values():
        fraction = (abs(value - avgDistance)/avgDistance)
        if fraction > leeway :
            print("imbalanced %s fraction: %f" % (json.dumps(scoreboard), fraction))
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
    print("count %i, magick nr size: %i, games played %i" % (
        balcount, currentGameCount-change, (currentGameCount-change)*balcount
    ))
    if balcount == acceptedMinimum:
        break

print("Magick number is %i" % currentGameCount)

