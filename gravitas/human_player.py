#!/usr/bin/env python

# This is not needed if you have PGU installed
import sys
sys.path.insert(0, "..")

import math
import time
import pygame
import pgu
from pgu import gui, timer

#import local libs
import card

'''a function to generate a Visual card with a widget(Table)'''    
def genVcard(cardName,cardValue,cardType):
    vcard = gui.Table()
    
    vcard.add(gui.Label(' '))
    vcard.tr()
    vcard.add(gui.Label(' '))
    vcard.add(gui.Label(cardValue))
    vcard.tr()
    vcard.add(gui.Label(' '))
    vcard.add(gui.Label(cardName))
    vcard.tr()
    vcard.add(gui.Label(' '))
    vcard.add(gui.Label(cardType))
    vcard.tr()
    vcard.add(gui.Label(' '))
    return vcard

'''a function to delete the index stack from stacks, a stack including 2 cards, one face up and another face down'''
def delcard(stacks,index):
    stacks_bak = stacks
    stacks = []
    for i in range(len(stacks_bak)):
        if (i != index):
            stacks.append(stacks_bak[i])
    return stacks

'''Drafting Dialog which provide GUI supporting for human player select a stack of cards from stacks
   All stacks of cards are shown in the dialog, human player can select one of the stacks of cards, 
   and then press confirm button to confirm the selection'''        

class DraftingDialog(gui.Dialog):
    def __init__(self,stacks):
        title = gui.Label("Drafting")
        # create a container to show all un-distributed stacks of cards and confirm button
        self.c = c = gui.Container(width = 400, height = 400)
        
        # create a talbe(widget) to place all stack of cards
        self.tbl = tbl = gui.Table()
        tbl.tr()
        # crate a group of stacks for selection
        self.g = g = gui.Group(value=None)
        
        # generate all cards included in the input argument stacks
        # and place them on the table
        card = [None]*len(stacks)
        for i in range(len(stacks)):
            cardName  = stacks[i][0].getName()
            cardValue = str(stacks[i][0].getValue())
            cardType  = stacks[i][0].getType()
            if cardType == 0:
                cardTypeStr = 'Normal'
            elif cardType == 1:
                cardTypeStr = 'Repulsor'
            else: cardTypeStr = 'Tractor'
                
            card[i] = genVcard(cardName, cardValue, cardTypeStr)
            if (i % 4 == 0):
                tbl.tr()
                tbl.td(gui.Label('  '))
                tbl.tr()
            tbl.td(gui.Tool(g,card[i],value=i))
            tbl.td(gui.Label("    "))
        
        # monitor the event whether the selection change
        g.send(gui.CHANGE)
        def getGv(self):
            print(stacks[self.g.value][0].getName(), ' is selected')
        g.connect(gui.CHANGE,getGv,self)
        
        # add card talbe onto the container
        c.add(tbl,50,10)
        
        # create a confirm button for the human player to confirm his/her selection
        self.b = b = gui.Button("Confirm")
        def clsDialog(self):
            self.close()
            if self.g.value is not None:
                self.selectedItem = self.g.value
            else:
                self.selectedItem = 0
            #self.tbl.clear()
            print('finally select ', stacks[self.selectedItem][0].getName())
        
        b.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        c.add(b,380,380)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,c)

'''a class to create a playing dialog for the human player
   In drarting phase, the selected cards will apper in this dialog
   In playing phase, the human player will select a card to play from this dialog'''        
class PlayingDialog(gui.Dialog):
    def __init__(self,stacks):
        title = gui.Label("Playing")
        # create a container to show all un-distributed stacks of cards and confirm button
        self.c = c = gui.Container(width = 400, height = 130)
        
        # create a talbe(widget) to place all cards
        self.tbl = tbl = gui.Table()
        tbl.tr()
        # crate a group of stacks for selection
        self.g = g = gui.Group(value=None)
        
        # generate all cards included in the input argument stacks
        # and place them on the table
        card = [None]*6
        for i in range(6):
            cardName  = stacks[i][0].getName()
            cardValue = str(stacks[i][0].getValue())
            cardType  = stacks[i][0].getType()
            if cardType == 0:
                cardTypeStr = 'Normal'
            elif cardType == 1:
                cardTypeStr = 'Repulsor'
            else: cardTypeStr = 'Tractor'
                
            card[i] = genVcard(cardName, cardValue, cardTypeStr)
            tbl.td(gui.Tool(g,card[i],value=i))
            tbl.td(gui.Label("    "))
        
        # monitor the event whether the selection change
        g.send(gui.CHANGE)
        def getGv(self):
            print(stacks[self.g.value][0].getName(), ' is selected')
        g.connect(gui.CHANGE,getGv,self)
        
        # add card talbe onto the container
        c.add(tbl,10,10)
        
        # create a confirm button for the human player to confirm his/her selection
        self.b = b = gui.Button("Confirm")
        def clsDialog(self):
            if self.g.value is not None:
                self.selectedItem = self.g.value
            else:
                self.selectedItem = 0
            #self.tbl.clear()
            print('finally select ', stacks[self.selectedItem][0].getName())
        
        b.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        c.add(b,380,120)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,c)

class App(gui.Desktop):
    def __init__(self,**params):
        gui.Desktop.__init__(self,**params)
    
        self.connect(gui.QUIT,self.quit,None)
    
        c = gui.Container(width=800,height=800)
        # create a Deck
        deck = card.Deck()
        # reshuffle 2*3*playerAmount cards 
        playerAmount = 4;
        self.stacks = stacks = deck.createCardField(playerAmount)
        self.draft_dialog = DraftingDialog(self.stacks)
        def ddq(self):
            self.stacks = delcard(self.stacks,self.draft_dialog.g.value)
            print('The latest length of the stacks is ', len(self.stacks))
        
        self.draft_dialog.b.connect(gui.CLICK,ddq,self)
        
        play_dialog = PlayingDialog(self.stacks)
        c.add(play_dialog,100,680)

        # create a button to open the drating dialog        
        b = gui.Button('Open Drafting Dialog')
        b.connect(gui.CLICK,self.draft_dialog.open,None)
        c.add(b,400,650)
        
        self.widget = c
                
        
        
app = App()
app.run()

        
        