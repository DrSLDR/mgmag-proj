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

# define globle parameters
class params:
    FACE_UP = 0
    FACE_DOWN = 1

'''a function to generate a Visual card with a widget(Table)'''    
def genVcard(cardName,cardValue,cardType):
    vcard = gui.Table(width = 30)
    
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

'''a function to generate visual Emergency Stop card return as a widget(Table)'''
def genEsCard(face_sta):
    if face_sta == params.FACE_UP:
        vcard = gui.Button("ES Card", width = 80, height = 90)
    else:
        vcard = gui.Button(" ", width = 80, height = 100)
        
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
        self.stacks = stacks
        # create a container to show all un-distributed stacks of cards and confirm button
        self.c = c = gui.Container(width = 400, height = 400)
        def genCardTbl(self,stacks):
        # create a talbe(widget) to place all stack of cards
            tbl = gui.Table()
            # create a group of stacks for selection
            self.g = gui.Group(name = 'drafting',value=None)
                  
            # generate all cards included in the input argument stacks
            # and place them on the table
            print('The latest length of the stacks is ', len(stacks))
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
                tbl.td(gui.Tool(self.g,card[i],value=i))
                tbl.td(gui.Label("    "))
                
            # monitor the event whether the selection change
            self.g.send(gui.CHANGE)
            def getGv(self):
                print(stacks[self.g.value][0].getName(), ' is selected')
            self.g.connect(gui.CHANGE,getGv,self)
            return tbl
        
        self.tbl = genCardTbl(self,self.stacks)
        # add card talbe onto the container
        self.c.add(self.tbl,50,10)
        
        # create a confirm button for the human player to confirm his/her selection
        self.b = b = gui.Button("Confirm")
            
        def clsDialog(self):
            if self.g.value is not None:
                self.selectedItem = self.g.value
            else:
                self.selectedItem = 0
            #self.tbl.clear()
            #self.c.remove(self.tbl)
            self.preStacks = self.stacks
            self.stacks = delcard(self.stacks,self.g.value)
            self.c.remove(self.tbl)
            self.tbl = genCardTbl(self,self.stacks)
            self.c.add(self.tbl,50,10)
            #self.close()
        
        b.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        self.c.add(self.b,380,380)
        self.c.repaint(self.b)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,self.c)
        

'''a class to create a playing dialog for the human player
   In drarting phase, the selected cards will apper in this dialog
   In playing phase, the human player will select a card to play from this dialog'''        
class PlayingDialog(gui.Dialog):
    def __init__(self,cards,EsUse):
        self.cards = cards
        self.EsUse = EsUse
        
        title = gui.Label("Playing")
        # create a container to show all un-distributed stacks of cards and confirm button
        self.c = c = gui.Container(width = 700, height = 150)
        
        def genCardTbl(self,cards):
            # create a talbe(widget) to place all cards
            tbl = gui.Table()
            # crate a group of stacks for selection
            self.g = g = gui.Group(value=None)
            # generate all cards included in the input argument stacks
            # and place them on the table
            amountCards = len(cards)
            if amountCards > 0:
                card = [None]*amountCards
                for i in range(amountCards):
                    cardName  = cards[i].getName()
                    cardValue = str(cards[i].getValue())
                    cardType  = cards[i].getType()
                    if cardType == 0:
                        cardTypeStr = 'Normal'
                    elif cardType == 1:
                        cardTypeStr = 'Repulsor'
                    else: cardTypeStr = 'Tractor'
                        
                    card[i] = genVcard(cardName, cardValue, cardTypeStr)
                    tbl.td(gui.Tool(g,card[i],value=i))
                    tbl.td(gui.Spacer(width = 10, height = 20))
                # monitor the event whether the selection change
                self.selected = False
                self.g.send(gui.CHANGE)
                def getGv(self):
                    print(cards[self.g.value].getName(), ' is selected')
                    self.selected = True
                self.g.connect(gui.CHANGE,getGv,self)
            return tbl
        
        
        # create a talbe(widget) to place all cards
        self.tbl = genCardTbl(self,self.cards)
        
        # crate a table(widget) to place emergency stop card
        self.esCardTbl = genEsCard(self.EsUse)
        
        # add card talbe onto the container
        self.c.add(self.tbl,10,10)
        self.c.add(self.esCardTbl,550,10)
        
        # create a confirm button for the human player to confirm his/her selection
        self.b = b = gui.Button("Confirm")
        def clsDialog(self):
            if self.g.value is not None:
                self.selectedItem = self.g.value
            else:
                self.selectedItem = 0
            if len(self.cards) > 0 and self.selected:
                print('finally select ', self.cards[self.selectedItem].getName())
                self.cards = delcard(self.cards,self.selectedItem)
                print('the new length of cards is', len(self.cards))
                self.c.remove(self.tbl)
                self.tbl = genCardTbl(self,self.cards)
                self.c.add(self.tbl,10,10)
                self.selected = False
            elif len(self.cards) == 0:
                print('There is no card to play')
            elif not self.selected:
                print('you should select one card')
            
        b.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        c.add(self.b,380,120)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,c)
        
class EsDialog(gui.Dialog):
    def __init__(self):
        # 1. define the title of the dialog
        title = gui.Label('Emergency Stop')
        # 2. define the container of the dialog
        c = gui.Container(width = 400, heigt = 300)
        # 2.1 create a label in container
        lb = gui.Label('Do you want to use Emergency Stop Card?')
        lbw,lbh = lb.resize()
        c.add(lb,int((400-lbw)/2),20)
        # 2.2 create a table with 'yes' or 'no' option in container and also a gruop for selection
        tbl = gui.Table()
        tbl.tr()
        g = gui.Group(value=0)
        tbl.td(gui.Tool(g,gui.Label('Yes'),value = 1))
        tbl.td(gui.Spacer(width = 50,height = 20))
        tbl.td(gui.Tool(g,gui.Label('No'),value = 0))
        tblw,tblh = tbl.resize()
        c.add(tbl,int((400-tblw)/2),20+lbh+20)
        g.send(gui.CHANGE)
        def gv(self):
            self.EsUsed = g.value
        g.connect(gui.CHANGE,gv,self)
        
        # create a confirm button to confirm selection 
        self.b = gui.Button("Confirm")
        def cEsD(self):
            print('ES WINDOW SELECTION IS ', self.EsUsed)
        
        self.b.connect(gui.CLICK,cEsD,self)
        # add confirm button to container
        c.add(self.b,160,100)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,c)
        
class App(gui.Desktop):
    def __init__(self,**params):
        gui.Desktop.__init__(self,**params)
        
        self.connect(gui.QUIT,self.quit,None)
    
        self.EsUsed = 0
        self.c = gui.Container(width=800,height=750)
        # create a Deck
        deck = card.Deck()
        # reshuffle 2*3*playerAmount cards 
        playerAmount = 4;
        self.stacks = stacks = deck.createCardField(playerAmount)
        
        # create draft dialog window
        self.draft_dialog = DraftingDialog(self.stacks)
        # get the size of draft dialog window
        self.ddw,self.ddh = self.draft_dialog.resize()
        
        # when the human player press 'confirm' button to confirm his/her selection, then
        # 1. close the drafting dialog
        # 2. if the amount of remain cards in playing window is less than 4, then
        #    2.1 copy the cards from playing window
        #    2.2 append selected stack (2 cards) into cards set which will be shown in playing window
        #    2.3 re-build the playing window with new cards
        def ddq(self):
            self.c.remove(self.draft_dialog)
            if len(self.play_dialog.cards) <= 4:
                # append the selected cards in drafting window into playing window
                self.play_dialog.cards.append(self.draft_dialog.preStacks[self.draft_dialog.selectedItem][0])
                self.play_dialog.cards.append(self.draft_dialog.preStacks[self.draft_dialog.selectedItem][1])
                # re-build the playing window with new cards
                self.c.remove(self.play_dialog)
                self.play_dialog = PlayingDialog(self.play_dialog.cards,self.EsUsed)
                self.c.add(self.play_dialog,50,self.ddh + 100)
        self.draft_dialog.b.connect(gui.CLICK,ddq,self)
        
        
        
        
        # crate initial playing window without card 
        self.play_dialog = PlayingDialog([],self.EsUsed)
        self.c.add(self.play_dialog,50,self.ddh + 100)

        # create a button to open the drating dialog        
        b = gui.Button('Open Drafting Dialog')
        def ddo(self):
            self.c.add(self.draft_dialog,int((800 - self.ddw)/2),30)
        b.connect(gui.CLICK,ddo,self)
        self.c.add(b,200,30 + self.ddh + 20)
        
        # create a button to test emergency stop card function
        self.Es_Dialog =  EsDialog()
        bes = gui.Button('Open Emergency Stop Dialog')
        def eso(self):
            print('kkk')
            self.c.add(self.Es_Dialog,100,100)
        bes.connect(gui.CLICK,eso,self)
        self.c.add(bes,400,30 + self.ddh + 20)
        
        def cesd(self):
            self.c.remove(self.Es_Dialog)
            self.EsUsed = self.Es_Dialog.EsUsed
            # re-build the playing window with new cards
            self.c.remove(self.play_dialog)
            self.play_dialog = PlayingDialog(self.play_dialog.cards,self.EsUsed)
            self.c.add(self.play_dialog,50,self.ddh + 100)            
            
        
        self.Es_Dialog.b.connect(gui.CLICK,cesd,self)
        
        self.widget = self.c
       
# *********************************************************          
# Main
# *********************************************************          
if __name__ == '__main__':
    app = App()
    app.run()

        
        