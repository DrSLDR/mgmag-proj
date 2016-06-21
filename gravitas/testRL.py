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

currentGameCount = 4 # the amount of games we test
change = 4 # how much to increase currentGameCount next time
leeway = 0.05 # fraction of deviation allowed

args = main.parser.parse_args(['-c', 'conf/rlAnd3Rand.json', '--headless', '-l', '0'])
factory = Factory(args)

playerCount = len(factory.createState().players)

def isBalanced(gameCount):
    #if not gameCount % playerCount == 0:
    #    raise ValueError("game count %i has to be devidable by playercount %i" % (gameCount, playerCount))
    scoreboard = dict((p,0) for p in factory.createState().players)
    avgDistance = 0
    for i in range(0,gameCount):
        scores = main.run(factory)
        #if i % (gameCount/100) == 0:
        #    print(int(i/(gameCount/100)),'%', end=" ")
        for score in scores:
            scoreboard[score[0]] += score[1]/gameCount
            avgDistance += (score[1]/playerCount)/gameCount
    i = 0
    score = len(scoreboard.items()) * [None] 
    for x in scoreboard.items():
        #print(x[0],'gets ', x[1])
        score[i] = [x[0],x[1]]
        i += 1
        
    return score


names = playerCount*['']
winCnts = playerCount*[0]
for j in range(25*3):
    print('*********************** ', j, ' *****************************')
    for i in range(400):
        #print('*********************** ', i, ' *****************************')
        score = isBalanced(1)
        
        if i == 0:
            for j in range(playerCount):
                names[j] = score[j][0]
        
        pos = playerCount*[0]
        for j in range(playerCount):
            pos[j]= score[j][1]
        
        maxPos = max(pos)
        maxPosIndex = pos.index(maxPos)
        winCnts[maxPosIndex] += 1
    
    for name,winCnt in zip(names,winCnts):
        print('agent ',name, ' wins ', winCnt, ' times' )
    
    
    #if i == 0:
    #    scoreList[0].append(score[0][0])
    #    scoreList[1].append(score[1][0])
    #    scoreList[2].append(score[2][0])
    #    scoreList[3].append(score[3][0])
    #    
    #scoreList[0].append(score[0][1])
    #scoreList[1].append(score[1][1])
    #scoreList[2].append(score[2][1])
    #scoreList[3].append(score[3][1])
 
#with open('score.json','w') as file:
#    json.dump(scoreList,file)



#while True:
#    balcount = 0
#    for _ in range(0,acceptedMinimum):
#        # output the information we need for statistics
#        if not isBalanced(currentGameCount):
#            currentGameCount += change
#            break
#        balcount += 1
#    print("count %i, magick nr size: %i, games played %i" % (
#        balcount, currentGameCount-change, (currentGameCount-change)*balcount
#    ))
#    if balcount == acceptedMinimum:
#        break
#

