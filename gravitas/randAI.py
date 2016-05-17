#!/usr/bin/env python

# This is not needed if you have PGU installed
import sys
sys.path.insert(0, "..")

import math
import time
import pygame
from pygame.locals import *
import pgu
from pgu import gui, timer
import random

#import local libs
import card
import strings
import human_player
from human_player import *

class randAI():
    def __init__(self,playerName):
        # initialize parameter
        self.EsUsed = 0                 # whether Emergency Stop card is used, 0: not used, 1: used
        self.stacks = []                # stacks which will be displayed in drafting window
        self.playingCards = []          # current cards which hold by the player
        self.playerName = playerName    # the name of player   
        self.cur_loc = 0
        
        
    # define methods for gameAI
    def DecisionMaking_Drafting(self,stacks):
        # get the amount of stack
        amountStacks = len(stacks)
        # random select a stack
        self.selectedStack = random.randint(0,amountStacks - 1)
        # append the selected cards into playingCards which is the card database of the gameAI
        self.playingCards.append(stacks[self.selectedStack][0])
        self.playingCards.append(stacks[self.selectedStack][1])
        return self.selectedStack

    def DecisionMaking_Playing(self):
        # Get the amount of card
        amountCards = len(self.playingCards)
        # ramdom select a card
        self.selectedCard = random.randint(0,amountCards - 1)
        # delete the selected card from playingCards database
        print(self.playerName, ' played ', self.playingCards[self.selectedCard].getName())
        self.playingCards = general.delcard(self.playingCards,self.selectedCard)
        return self.selectedCard
    
    def DecisionMaking_ES(self,locationInf):
        # get the player's self location
        pre_loc = self.cur_loc
        self.cur_loc = locationInf
        if self.cur_loc < pre_loc and abs(self.cur_loc - pre_loc) > int(len(self.playingCards)/1.5):
            self.selectedEs = 1
            print(self.playerName, ' choose to use Emergency Stop since pre_loc is ', pre_loc, ' and cur_loc is ', self.cur_loc, 
                  'and he/she has ', len(self.playingCards), 'cards in hand')
        else:
            self.selectedEs = 0
            print(self.playerName, ' choose to not use Emergency Stop since pre_loc is ', pre_loc, ' and cur_loc is ', self.cur_loc, 
                  'and he/she has ', len(self.playingCards), 'cards in hand')
        return self.selectedEs
        
        
        
        
# test code
if __name__ == '__main__':
    # create a Deck
    deck = card.Deck()
    # reshuffle 2*3*playerAmount cards 
    playerAmount = 4;
    playerName_0 = 'Andy'
    playerName_1 = 'July'
    playerName_2 = 'Salary'
    playerName_3 = 'Alan'
    
    # -----------------------------------------------
    # step1. create a human player
    # -----------------------------------------------
    AIPlayer = randAI(playerName_0)
    stacks = deck.createCardField(playerAmount)
    
    selectedStack = AIPlayer.DecisionMaking_Drafting(stacks)
    print(playerName_0, 'selected ', stacks[selectedStack][0].getName(), ' and ', stacks[selectedStack][1].getName())
    selectedStack = AIPlayer.DecisionMaking_Drafting(stacks)
    print(playerName_0, 'selected ', stacks[selectedStack][0].getName(), ' and ', stacks[selectedStack][1].getName())
    selectedStack = AIPlayer.DecisionMaking_Drafting(stacks)
    print(playerName_0, 'selected ', stacks[selectedStack][0].getName(), ' and ', stacks[selectedStack][1].getName())
    selectedCard = AIPlayer.DecisionMaking_Playing()
    AIPlayer.DecisionMaking_ES(3)
    selectedCard = AIPlayer.DecisionMaking_Playing()
    AIPlayer.DecisionMaking_ES(1)
    selectedCard = AIPlayer.DecisionMaking_Playing()
    AIPlayer.DecisionMaking_ES(7)
    selectedCard = AIPlayer.DecisionMaking_Playing()
    AIPlayer.DecisionMaking_ES(2)
    selectedCard = AIPlayer.DecisionMaking_Playing()
    AIPlayer.DecisionMaking_ES(5)
    selectedCard = AIPlayer.DecisionMaking_Playing()