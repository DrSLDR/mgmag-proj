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

#import local libs
import card
import strings

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
    def __init__(self,stacks,playerName):
        # 1. get input arguments
        self.stacks = stacks
        self._playerName = playerName
        # 2. load audios
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        # 3. create the drafting window which includes a lable and a container
        # 3.1 crate the lable 
        lableStr = 'Drafing Window for ' + self._playerName;
        title = gui.Label(lableStr)
        # 3.2 create a container to show all un-distributed stacks of cards and confirm button
        self._c = c = gui.Container(width = 400, height = 400)
        def genCardTbl(self,stacks):
        # create a talbe(widget) to place all stack of cards
            tbl = gui.Table()
            # create a group of stacks for selection
            self.g = gui.Group(value=None)
            # generate all cards included in the input argument stacks
            # and place them on the table
            print('The latest length of the stacks is ', len(stacks))
            card = [None]*len(stacks)
            for i in range(len(stacks)):
                # get the card information
                cardName  = stacks[i][0].getName()
                cardValue = str(stacks[i][0].getValue())
                cardType  = stacks[i][0].getType()
                if cardType == 0:
                    cardTypeStr = 'Normal'
                elif cardType == 1:
                    cardTypeStr = 'Repulsor'
                else: cardTypeStr = 'Tractor'
                # create the image of each card as a table(widgit)
                card[i] = genVcard(cardName, cardValue, cardTypeStr)
                # 4 cards in one row
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
                self._click.play()
            self.g.connect(gui.CHANGE,getGv,self)
            return tbl
        
        self.tbl = genCardTbl(self,self.stacks)
        # add card talbe onto the container
        self._c.add(self.tbl,50,10)
        
        # create a confirm button for the human player to confirm his/her selection
        self.b = cb = gui.Button("Confirm")
        
        # define the the things need to do before close the drafting window
        def clsDialog(self):
            # get the final selected item 
            self._selectedItem = self.g.value
            # play the confirm audio
            self._confirm.play()
        
        cb.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        self._c.add(cb,380,380)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,self._c)
    
    def getSelectedItem(self):
        return self._selectedItem
        
    def getConfirmButton(self):
        return self.b

'''a class to create a playing dialog for the human player
   In drarting phase, the selected cards will apper in this dialog
   In playing phase, the human player will select a card to play from this dialog'''        
class PlayingDialog(gui.Dialog):
    def __init__(self,cards,EsUse,playerName):
        # 1. initialize
        self.cards = cards
        self.EsUse = EsUse
        self._playerName = playerName
        # 2. load audios
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        
        lableStr = 'Playing Window for ' + self._playerName;
        title = gui.Label(lableStr)
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
                    self._click.play()
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
                print('the new length of cards is', len(self.cards))
                #self.c.remove(self.tbl)
                #self.tbl = genCardTbl(self,self.cards)
                #self.c.add(self.tbl,10,10)
                self.selected = False
            elif len(self.cards) == 0:
                print('There is no card to play')
            elif not self.selected:
                print('you should select one card')
            self._confirm.play()
            
        b.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        c.add(self.b,380,120)
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,c)
    
    def getSelectedItem(self):
        return self.selectedItem
        
class EsDialog(gui.Dialog):
    def __init__(self,playerName):
        self._playerName = playerName
        self.EsUsed = 0
        # load audios
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        # 1. define the title of the dialog
        lableStr = 'Emergency Stop Window for ' + self._playerName;
        title = gui.Label(lableStr)
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
            self._click.play()
        g.connect(gui.CHANGE,gv,self)
        
        # create a confirm button to confirm selection 
        self.b = gui.Button("Confirm")
        def cEsD(self):
            print('ES WINDOW SELECTION IS ', self.EsUsed)
            self._confirm.play()
        self.b.connect(gui.CLICK,cEsD,self)
        
        # add confirm button to container
        c.add(self.b,160,100)
        # initialie Emergency Sop dialog
        gui.Dialog.__init__(self,title,c)
    
    def getEsUsed(self):
        return self.EsUsed
        
        
class humanPlayer():
    def __init__(self,playerName,c):
        # initialize parameter
        self.EsUsed = 0                 # whether Emergency Stop card is used, 0: not used, 1: used
        self.stacks = []                # stacks which will be displayed in drafting window
        self.playingCards = []          # current cards which hold by the player
        self.c = c                      # the container
        self.playerName = playerName    # the name of player   
        self.ddx,self.ddy = 160,30      # the left top location of draft dialog
        self.pdx,self.pdy = 40,550      # the left top location of playing dialog
        self.esdx,self.esdy = 100,100   # the left top location of Emergency Stop dialog
        
        # *******************************************************
        # crate initial Drafting window without card 
        # *******************************************************
        self.draft_dialog = DraftingDialog(self.stacks,self.playerName)
        
        # *******************************************************
        # crate initial playing window without card 
        # *******************************************************
        self.play_dialog = PlayingDialog(self.playingCards,self.EsUsed,self.playerName)
        self.startPlayDialog()           
        
        # *******************************************************
        # crate initial Emergency Stop window without card 
        # *******************************************************
        self.Es_Dialog =  EsDialog(self.playerName)
        def esq(self):
            self.c.remove(self.Es_Dialog)
            self.EsUsed = self.Es_Dialog.getEsUsed()
        self.Es_Dialog.b.connect(gui.CLICK,esq,self)
    
    # ***********************************************************
    # define methods for human player    
    # ***********************************************************
    def setStacks(self,stacks):
        self.stacks = stacks
    def setEsUsed(self,EsUsed):
        self.EsUsed = EsUsed
    
    def startDraftDialog(self):
        if self.c.find(self.draft_dialog):
            self.c.remove(self.draft_dialog)
        self.draft_dialog = DraftingDialog(self.stacks,self.playerName)
        self.c.add(self.draft_dialog,self.ddx,self.ddy)
        # when the human player press 'confirm' button to confirm his/her selection, then
        # 1. close the drafting dialog
        # 2. if the amount of remain cards in playing window is less than 4, then
        #    2.1 copy the cards from playing window
        #    2.2 append selected stack (2 cards) into cards set which will be shown in playing window
        #    2.3 re-build the playing window with new cards
        def ddq(self):
            if self.draft_dialog.getSelectedItem() != None:
                self.c.remove(self.draft_dialog)
                if len(self.play_dialog.cards) <= 4:
                    # append the selected cards in drafting window into playing window
                    self.playingCards.append(self.stacks[self.draft_dialog.getSelectedItem()][0])
                    self.playingCards.append(self.stacks[self.draft_dialog.getSelectedItem()][1])
                    # update the playing window with new cards
                    self.startPlayDialog()
        ddConfirmButton = self.draft_dialog.getConfirmButton()
        ddConfirmButton.connect(gui.CLICK,ddq,self)
    
    def startPlayDialog(self):
        if self.c.find(self.play_dialog):
            self.c.remove(self.play_dialog)
        self.play_dialog = PlayingDialog(self.playingCards,self.EsUsed,self.playerName)
        self.c.add(self.play_dialog,self.pdx,self.pdy)            
        def pdq(self):
            print('test')
            self.playingCards = delcard(self.playingCards,self.play_dialog.getSelectedItem())
            # update the playing window with new cards
            self.c.remove(self.play_dialog)
            self.play_dialog = PlayingDialog(self.playingCards,self.EsUsed,self.playerName)
            self.play_dialog.b.connect(gui.CLICK,pdq,self)
            self.c.add(self.play_dialog,self.pdx,self.pdy)
        self.play_dialog.b.connect(gui.CLICK,pdq,self)
        
    def startEsDialog(self):
        self.c.add(self.Es_Dialog,self.esdx,self.esdy)
        
    def getSelectedStack(self):
        return self.draft_dialog.getSelectedItem()
    
    def getSelectedCard(self):
        return self.play_dialog.getSelectedItem()
        
    def getSelectedEs(self):
        return self.Es_dialog.getEsUsed()
    
    def getDraftDialogConfirmButton(self):
        return self.draft_dialog.getConfirmButton()
    
    def getEsUsed(self):
        return self.EsUsed
        
# *********************************************************          
# Main
# ********************************************************* 
'''the class App is an example of how to use humanPlayer class'''
class App(gui.Desktop):
    def __init__(self):
        # initilize the gui
        gui.Desktop.__init__(self)
        self.connect(gui.QUIT,self.quit,None)
        
        # crate a container in APP
        self.c = gui.Container(width=800,height=750)
        
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
        self.humanPlayer_0 = humanPlayer(playerName_0,self.c)
        self.EsUsed = 0
        self.stacks = stacks = deck.createCardField(playerAmount)
    
        # create a button to open the drating dialog        
        b = gui.Button('Open Drafting Dialog')
        def ddo(self):
            self.humanPlayer_0.setStacks(self.stacks)
            self.humanPlayer_0.startDraftDialog()
            # the game manager should monitor the confirm event from drafting dialog
            def ddq(self):
                self.stacks = delcard(self.stacks,self.humanPlayer_0.getSelectedStack())
                print('draft dialog closed, the latest amount of stacks is ', len(self.stacks))
            self.hp0_ddcb = self.humanPlayer_0.draft_dialog.getConfirmButton()
            self.hp0_ddcb.connect(gui.CLICK,ddq,self)
        b.connect(gui.CLICK,ddo,self)
        self.c.add(b,200,500)
        #self.hp0_ddcb = self.humanPlayer_0.getDraftDialogConfirmButton()
        
        # create a button to test emergency stop card function
        bes = gui.Button('Open Emergency Stop Dialog')
        def eso(self):
            self.humanPlayer_0.startEsDialog()
            
        bes.connect(gui.CLICK,eso,self)
        self.c.add(bes,400,500)
        
        def cesd(self):
            self.EsUsed = self.humanPlayer_0.getEsUsed()
            # re-build the playing window with new cards
            self.humanPlayer_0.setEsUsed(self.EsUsed)
            self.humanPlayer_0.startPlayDialog()
        self.humanPlayer_0.Es_Dialog.b.connect(gui.CLICK,cesd,self)
        
        self.widget = self.c
        
if __name__ == '__main__':
    app = App()
    app.run()

        
        