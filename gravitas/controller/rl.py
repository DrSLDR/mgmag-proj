"""Reinforcement Learning AI implementation."""

import random
import math
import json
from .interface import IPlayerController
from model.card import Card

class QL:
    ''' Q Learning model for reinforcement learning gameAI'''
    def __init__(self):
        # load Q values from file at the beginning of each run
        with open('controller/QData/QLModel.json') as file:
            self._Qvalue = json.load(file)
        self._stateActionHistoryList = []
        self._ESenable = True
        
    def updateQ(self,learningRate,discountFactor,currPositions,nextPositions,selfLoc,cardName, reward):
        '''update Q(s,a) for a single move with the formula:
        Q(s,a) <- (1 - learningRate) * Q(s,a) + learningRate * (r + discountFactor * maxQ(s',a'))        '''
        currStateIndex = self._genStateIndex(currPositions, selfLoc)
        nextStateIndex = self._genStateIndex(nextPositions, selfLoc)
        currActionIndex = self._genActionIndex(cardName)
        Qsa = self._Qvalue[currStateIndex][currActionIndex]
        Qsa =  (1 - learningRate) * Qsa + learningRate * (reward + discountFactor * self._getMaxStateActionValue(nextStateIndex))
        self._Qvalue[currStateIndex][currActionIndex] = Qsa
        return True
    
    def roundupdateQ(self,round,turn,selfLoc,history,learnWholeRound,opponetsPlayedTractor,gameOver):
        '''record the (s,a) in a whole round, and update Q(s,a) for all moves at the end of each round'''
        if (turn == 0) or gameOver:
            if (round > 0) and opponetsPlayedTractor == False:
                self._stateActionHistoryList.append(history)
                lenHistoryList = len(self._stateActionHistoryList)
                for i in range(lenHistoryList - 1):
                    if learnWholeRound == True:                   
                    # calculate the reward for the whole round, only the last move get a immediate reward
                    # the immediate reward for all other moves are 0
                    # the first 5 moves update their Q value via nextState value
                        if i == 0 :
                            reward = self._stateActionHistoryList[lenHistoryList-1][0][selfLoc] - self._stateActionHistoryList[0][0][selfLoc]
                            discountFactor = 0.7
                        else:
                            reward = 0
                            discountFactor = 0.9
                    # calculate the reward for each move                    
                    else: 
                        reward = self._stateActionHistoryList[lenHistoryList-1-i][0][selfLoc] - self._stateActionHistoryList[lenHistoryList-2-i][0][selfLoc]
                        discountFactor = 0.2
                    
                    # negatively reinforce reward by n times to teach gameAI avoid actions with negative rewards
                    if (reward < 0): reward = reward * 10 
                    
                    # get state,action(normal card and ES card),nextState from history
                    currPositions = self._stateActionHistoryList[lenHistoryList-2-i][0]
                    currAction = self._stateActionHistoryList[lenHistoryList-2-i][1]
                    nextPositions = self._stateActionHistoryList[lenHistoryList-1-i][0]
                    # update the Q(s,a)
                    self.updateQ(0.7, discountFactor,currPositions, 
                                nextPositions, 
                                selfLoc, 
                                currAction, 
                                reward)
                    
            self._stateActionHistoryList = []
        # record the two-tuple set (state,action), nextState and reward can be calculated from the history sets
        self._stateActionHistoryList.append(history)
        return True
        
    def chooseAction(self,turn,currPositions,selfLoc,cards,coeff_T = 10):
        '''choose action for each move'''
        # Enabe to Use Emergency Stop card at the beginning of each round
        # set self._ESenable to False at the beginning of each round makes AI ignore ES card
        # generate stateIndex from current positions of all players
        stateIndex = self._genStateIndex(currPositions, selfLoc)
        # calculate the exponential value of Q(s,a)/T
        expQvalueList = []
        for card in cards:
            actionIndex = self._genActionIndex(card.getName())
            Qvalue = self._getQstateActionValue(stateIndex,actionIndex)
            expQvalue = math.exp(Qvalue/coeff_T)
            expQvalueList.append(expQvalue)
        # calculate the probability with Boltzmann distribution prob(a|s) = exp(Q(s,a)/T)/sum(exp(Q(s,a'))) 
        probs = []
        sumExpQvalue = sum(expQvalueList)
        for value in expQvalueList:
            prob = value / sumExpQvalue
            probs.append(prob)
        # select a card use Boltzmann distribution, the card with higher probability has higher opportunity to be selected
        selectedCard = self._probRandomPick(cards, probs)
        #selectedCard = self._probMaxPick(cards, probs)
        return selectedCard
    
    def saveQLModel2file(self):
        ''' save the Q values into file'''
        with open('controller/QData/QLModel.json','w') as file:
            json.dump(self._Qvalue,file)
        
    def _genActionIndex(self,cardName):
        '''generate index for each action of playing card '''
        actionDict = { "Ar" :  0, "B"  :  1, "C"  :  2, "Dy" :  3, "Es" :  4, "F"  :  5, "Ga" : 6,
                       "H"  :  7, "Ir" :  8, "Jo" :  9, "Kr" : 10, "Li" : 11, "Mg" : 12, "Ne" : 13,
                       "O"  : 14, "Pu" : 15, "Qt" : 16, "Ra" : 17, "Si" : 18, "Th" : 19, "U"  : 20,
                       "V"  : 21, "W"  : 22, "Xe" : 23, "Y"  : 24, "Zr" : 25}
        # if no ES card, then the index for each card is from 0 to 25, for action with ES card, plus 26
        actionIndex = actionDict[cardName]
        return actionIndex
    
    def _genStateIndex(self,positions,selfLoc):
        ''' generate the index for each states'''
        # get self position
        selfPos = positions[selfLoc]
        # get the position of all other players in the backward direction
        # get the position of all other players in the forward direction
        forwardDistList = []
        backwardDistList = []
        for pos in positions:
            if pos < selfPos:
                backwardDistList.append(selfPos - pos)
            elif pos > selfPos:
                forwardDistList.append(pos - selfPos)
                
        # find the closet oppenent if forward direction
        if len(forwardDistList) > 0:
            if min(forwardDistList) <= 10:
                forwardClosestPos = min(forwardDistList)
            else:
                forwardClosestPos = 11
        else:
            forwardClosestPos = None
        
        # find the closet oppenent if backward direction
        if len(backwardDistList) > 0:
            if min(backwardDistList) <= 10:
                backwardClosestPos = min(backwardDistList)
            else:
                backwardClosestPos = 11
        else:
            backwardClosestPos = None
        
        # generate the game state with the relative postion of closest opponents in forward and backward direction 
        if forwardClosestPos is None and backwardClosestPos is None:
            stateIndex = 0
        elif forwardClosestPos is None and backwardClosestPos is not None:
            stateIndex = backwardClosestPos
        elif forwardClosestPos is not None and backwardClosestPos is None:
            stateIndex = forwardClosestPos + 11
        else:
            stateIndex = 22 + forwardClosestPos * backwardClosestPos
            
        return stateIndex

    def _getQstateActionValue(self,stateIndex,actionIndex):
        '''get the specific Q value by specifying state and action'''
        return self._Qvalue[stateIndex][actionIndex]
    
    def _getQstateValue(self,stateIndex):
        '''get a set of Q values by specifying state'''
        return self._Qvalue[stateIndex]
    
    def _getMaxStateActionValue(self,stateIndex):
        '''get a maximum Q value in a specific state'''
        maxValue = 0
        QstateValue = self._getQstateValue(stateIndex)
        for v in QstateValue :
            if v > maxValue:
                maxValue = v
        return maxValue
    
    def _probRandomPick(self,cards,probs):
        '''select a card with probability, the card with higher probability has more chance to be selected'''
        randomNum = random.uniform(0,1)
        cumulative_prob = 0.0
        for card,cardProb in zip(cards,probs):
            cumulative_prob += cardProb
            if cumulative_prob > randomNum:
                break
        return card
    
    def _probMaxPick(self,cards,probs):
        '''select a card with the maximum probability value'''
        maxProb = 0.0
        for  card,prob in zip(cards,probs):
            if (prob > maxProb):
                maxProb = prob
                selectedCard = card
        return selectedCard

class QL_ES:
    ''' Q Learning Emergency Stop model for reinforcement learning gameAI'''
    def __init__(self):
        # load Q values from file at the beginning of each run
        with open('controller/QData/QLModelES.json') as file1:
            self._QvalueES = json.load(file1)
        self._stateActionHistoryList = []
        
    def updateQ(self,learningRate,discountFactor,currStateSet,nextStateSet,UseEmergencyStopCard, reward):
        '''update Q(s,a) for a single move with the formula:
        Q(s,a) <- (1 - learningRate) * Q(s,a) + learningRate * (r + discountFactor * maxQ(s',a'))        '''
        currStateIndex = self._genStateIndex(currStateSet)
        nextStateIndex = self._genStateIndex(nextStateSet)
        currActionIndex = self._genActionIndex(UseEmergencyStopCard)
        Qsa = self._QvalueES[currStateIndex][currActionIndex]
        if currActionIndex == 1:
            # use ES, only immediate reward, no long term reward 
            Qsa =  (1 - learningRate) * Qsa + learningRate * reward
        else:
            # not use ES, only long term reward, no immediate reward
            Qsa =  (1 - learningRate) * Qsa + learningRate * discountFactor * self._getMaxStateActionValue(nextStateIndex)
        self._QvalueES[currStateIndex][currActionIndex] = Qsa
        return True
    
    def roundupdateQ(self,history):
        '''record the (s,a) in a whole round, and update Q(s,a) for all moves at the end of each round'''
        if history[0][0] == 5 or history[1] == True :
            self._stateActionHistoryList.append(history)
            for i in range(len(self._stateActionHistoryList)):
                # get current state                
                currStateSet = self._stateActionHistoryList[i][0]
                # get next state
                if i < (len(self._stateActionHistoryList) - 1):
                    nextStateSet = self._stateActionHistoryList[i+1][0]
                else:
                    nextStateSet = None
                # get current action from history
                useES = self._stateActionHistoryList[i][1]
                
                # get current reward 
                closestShipDirection = currStateSet[1]
                playedCard = currStateSet[2]
                if playedCard.getType() == Card.Type.normal:
                    if closestShipDirection == 0:
                        reward = -playedCard.getValue()
                    else:
                        reward = playedCard.getValue()
                else:
                    if closestShipDirection == 0:
                        reward = playedCard.getValue()
                    else:
                        reward = -playedCard.getValue()
                if useES:
                    reward = -reward
                else:
                    reward = 0
                
                # update the Q(s,a)
                self.updateQ(0.85, 0.95,
                            currStateSet, 
                            nextStateSet, 
                            useES, 
                            reward)
                
            self._stateActionHistoryList = []
        # record the two-tuple set (state,action), nextState and reward can be calculated from the history sets
        self._stateActionHistoryList.append(history)
        return True
        
    def chooseAction(self,currStateSet,coeff_T = 10):
        '''choose action for each move'''
        #turn = currStateSet[0]        
        #closestShipDirection = currStateSet[1]
        #playedCard = currStateSet[2]
        #playedCardType = playedCard.getType()
        #playedCardValue = playedCard.getValue()
        #if closestShipDirection == 0 and playedCardType == Card.Type.normal and playedCardValue > (5-turn):
        #    useES = True
        #elif closestShipDirection == 1 and playedCardType == Card.Type.repulsor and playedCardValue > (5-turn):
        #    useES = True
        #else:
        #    useES = False
        #return useES
            
        stateIndex = self._genStateIndex(currStateSet)
        # calculate the exponential value of Q(s,a)/T
        cards=[False,True]
        expQvalueList = []
        for card in cards:
            actionIndex = self._genActionIndex(card)
            Qvalue = self._getQstateActionValue(stateIndex,actionIndex)
            expQvalue = math.exp(Qvalue/coeff_T)
            expQvalueList.append(expQvalue)
        # calculate the probability with Boltzmann distribution prob(a|s) = exp(Q(s,a)/T)/sum(exp(Q(s,a'))) 
        probs = []
        sumExpQvalue = sum(expQvalueList)
        for value in expQvalueList:
            prob = value / sumExpQvalue
            probs.append(prob)
        # select a card use Boltzmann distribution, the card with higher probability has higher opportunity to be selected
        #selectedCard = self._probRandomPick(cards, probs)
        selectedCard = self._probMaxPick(cards, probs)
        return selectedCard
    
    def saveQLModel2file(self):
        ''' save the Q values into file'''
        with open('controller/QData/QLModelES.json','w') as file1:
            json.dump(self._QvalueES,file1)
        
    def _genActionIndex(self,UseEmergencyStopCard):
        '''generate index for each action of playing card '''
        # if no ES card, then the index for each card is from 0 to 25, for action with ES card, plus 26
        if UseEmergencyStopCard == False :               
            actionIndex = 0
        else:
            actionIndex = 1
        return actionIndex
    
    def _genStateIndex(self,currStateSet):
        ''' generate the index for each states'''
        if currStateSet is None:
            return None
        turn = currStateSet[0]
        closestShipDirect = currStateSet[1]
        playedCard = currStateSet[2]
        playedCardType = playedCard.getType()
        playedCardValue = playedCard.getValue() - 1
        stateIndex = 40 * turn + 20 * closestShipDirect + 10 * playedCardType + playedCardValue
        return stateIndex

    def _getQstateActionValue(self,stateIndex,actionIndex):
        '''get the specific Q value by specifying state and action'''
        return self._QvalueES[stateIndex][actionIndex]
    
    def _getQstateValue(self,stateIndex):
        '''get a set of Q values by specifying state'''
        return self._QvalueES[stateIndex]
    
    def _getMaxStateActionValue(self,stateIndex):
        '''get a maximum Q value in a specific state'''
        if stateIndex is None:
            return 0
        
        maxValue = 0
        QstateValue = self._getQstateValue(stateIndex)
        for v in QstateValue :
            if v > maxValue:
                maxValue = v
        return maxValue
    
    def _probRandomPick(self,cards,probs):
        '''select a card with probability, the card with higher probability has more chance to be selected'''
        randomNum = random.uniform(0,1)
        cumulative_prob = 0.0
        for card,cardProb in zip(cards,probs):
            cumulative_prob += cardProb
            if cumulative_prob > randomNum:
                break
        return card
    
    def _probMaxPick(self,cards,probs):
        '''select a card with the maximum probability value'''
        maxProb = 0.0
        for  card,prob in zip(cards,probs):
            if (prob > maxProb):
                maxProb = prob
                selectedCard = card
        return selectedCard
    
    

class RLAI_PC(IPlayerController):
    """player controller with build-in reinforcement learning AI """
    def __init__(self, player, args,container):
        super().__init__(player,args)
        self._QL = QL()
        self._QLES = QL_ES()
        self._opponentsPlayedTractor = False
        self._gameOver = False

    #def pollDraft(self, state):
    #    """Function that returns the choice of a stack from the draw field"""
    #    # Bind in the percieved fields
    #    percievedField = state.deck.percieveCardField()
    #    # if there are cards left on the field, choose a stack
    #    if not len(percievedField) == 0:
    #        fieldOfChoice = random.choice(percievedField)
    #        # returns the index of the choosen stack
    #        return fieldOfChoice[0]
    #    print("Oops, you are trying to choose a stack from an empty field") 
    #    
    #    return None

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        """RANDOM choice"""
        
        # Bind in the percieved fields
        percievedField = state.deck.percieveCardField()

        # just return if there are no fields left
        if len(percievedField) == 0:
            return None

        # if only one stack left, return that one
        if len(percievedField) == 1:
            return percievedField[0].index 

        ###### if more than one choice left:

        # get cards that you already have (your hand)
        hand = self.player.getHand()
        handTrac = [c for c in hand if c.getType() == Card.Type.tractor]
        handNormLow = [c for c in hand if c.getType() == Card.Type.normal and c.getValue() < 7]
        handNormHigh = [c for c in hand if c.getType() == Card.Type.normal and c.getValue() >= 3]
        handRep = [c for c in hand if c.getType() == Card.Type.repulsor]

        # order field options on card type
        tractors = [f for f in percievedField if f.card.getType() == Card.Type.tractor]
        normalHighs = [f for f in percievedField if f.card.getType() == Card.Type.normal and f.card.getValue() < 7]
        normalLows = [f for f in percievedField if f.card.getType() == Card.Type.normal and f.card.getValue() >= 3]
        repulsors = [f for f in percievedField if f.card.getType() == Card.Type.repulsor]

        # if there are tractors available, and you don't have one in your hand
        if len(tractors) > 0 and len(handTrac) == 0:
            return tractors[0].index
        # if there are repulsors, but you dont have them in your hand
        if len(repulsors) > 0 and len(handRep) == 0: 
            return repulsors[0].index

        # get lowest normal that plays first
        if len(normalLows) > 0 and len(handNormLow) == 0:
            lowFirstSorted = sorted(normalLows, key = lambda x:x.card.getName()[0])# sort on first letter
            return lowFirstSorted[0].index 

        # get highest normal that plays first
        if len(normalHighs) > 0 and len(handNormHigh) == 0:
            highFirstSorted = sorted(normalHighs, key = lambda x:x.card.getName()[0])# sort on first letter
            return highFirstSorted[0].index 

        # if nothin else works, just take a random field
        randomField = random.choice(percievedField)
        return randomField.index
    
    
    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        self._round = state.round
        self._turn = state.turn
        #print('-----------', self.player.getName(),  '---------------------------------')
        #print('Round = ',round, ' Turn = ',turn)
        # get the positions for all players from game state
        positions = []
        cnt = 0
        for p in state.players:
            playerName = state.getPlayer(p)[0].getName()
            playerPos  = state.getPlayer(p)[0].getPos()
            positions.append(playerPos)
            if self.player.getName() == playerName:
                self._selfLoc = cnt 
            cnt += 1
        # get the cards in hand 
        hand = self.player.getHand()
        # choose a card from cards in hand
        cardOfChoice = self._QL.chooseAction(self._turn,positions,self._selfLoc,hand,coeff_T = 3)
        
        # record the (state,action) as a history of current move 
        self._history = [positions,cardOfChoice.getName()]
        # update QL modle at each move
        self._QL.roundupdateQ(self._round, self._turn, self._selfLoc, self._history,False,self._opponentsPlayedTractor,self._gameOver)            
        if (self._turn == 0):
            self._opponentsPlayedTractor == False
        
        if not len(hand) == 0:
            # returns the choosen card here
            return cardOfChoice
        print("Oops, you are trying to play a card from an empty hand")
        return None

    #def pollEmergencyStop(self, state):
    #    """Function that returns the choice of using the emergency stop as a boolean"""
    #    doesPlayEmergencyStop = self._ESuse
    #    return doesPlayEmergencyStop
    
    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean.
        Right now the choice is rather egocentric; no other-player-bullying is done."""
        turn = state.turn
        # get closest ship
        targetName = state.getTarget(self.player.getName())
        if targetName is None:
            # player is stuck, don't waste ES!
            return False
        if self._playedCard.getType() == Card.Type.tractor:
            # choice of using ES with tractor cardType is complex...so dont
            return False
        # distance to closest ship (sign equals direction)
        target = state.getShip(targetName).ship
        distance = target.getPos() - self.player.getPos()
        # closestShip Direction, 0: backward 1: forward
        closestShipDirection = distance > 0
        # choose whether use Emergency Stop card 
        stateSet = [turn,closestShipDirection,self._playedCard]
        useES = self._QLES.chooseAction(stateSet)
        # update Q-values
        history = [stateSet,useES]
        self._QLES.roundupdateQ(history)

        return useES 
    
    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        return False
    
    def announceWinner(self, state):
        """Function that updates the PC after the last turn"""
        self._gameOver = True
        self._QL.roundupdateQ(self._round, self._turn, self._selfLoc, self._history,False, self._opponentsPlayedTractor,self._gameOver)            
        #self._QL.saveQLModel2file()
        #self._QLES.saveQLModel2file()
        
        return None
        
    def informReveal(self, cards):
        """The definitive set of played cards in a round are shown to the player"""
        self.log.info("Random ai informed about %s" % cards)
        self._reveal = cards
        self._playedCard = [c for c in cards if cards[c] == self.player.getName()][0] # find unique card owned by player        
        for card in cards:        
            if card.getType() == Card.Type.tractor and cards[card] != self.player.getName():
                self._opponentsPlayedTractor = True
