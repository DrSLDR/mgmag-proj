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
class general:
    '''a function to generate a Visual card with a widget(Table)'''    
    def genVcard(card):
        # get the card information
        cardName  = card.getName()
        cardValue = str(card.getValue())
        cardType  = card.getType()
        if cardType == 0:
            cardTypeStr = ' Normal  '
        elif cardType == 1:
            cardTypeStr = 'Repulsor'
        else: cardTypeStr = ' Tractor  '
        
        # create the card image as a table
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
        vcard.add(gui.Label(cardTypeStr))
        vcard.tr()
        vcard.add(gui.Label(' '))
        return vcard
    
    '''a function to generate visual Emergency Stop card return as a widget(Table)'''
    def genEsCard(face_sta):
        if face_sta == params.FACE_UP:
            vcard = gui.Button("ES Card", width = 75, height = 95, name = 'EsButton')
        else:
            vcard = gui.Button(" ", width = 75, height = 95, name = 'EsButton')
            
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
    # define the initial method
    def __init__(self,stacks,playerName):
        # 1. get input arguments
        self.stacks = stacks
        self._playerName = playerName
        # create a group of stacks for selection
        self.group = gui.Group(value=None)
        # 2. load audios
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        # 3. create the drafting window which includes a lable and a container
        # 3.1 crate the lable 
        lableStr = 'Drafing Window for ' + self._playerName;
        title = gui.Label(lableStr)
        # 3.2 create a container to show all un-distributed stacks of cards and confirm button
        self.stacksContainer = gui.Container(width = 500, height = 400)
        self.stacksTbl = gui.Table() 
        
        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        # define the the things need to do before close the drafting window
        def clsDialog(self):
            # get the final selected item 
            self._selectedItem = self.group.value
            # play the confirm audio
            self._confirm.play()
            if self._selectedItem is not None:
                self.stacksContainer.remove(self.stacksTbl)
                self.close()
        self.confirmButton.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        self.stacksContainer.add(self.confirmButton,300,370)
        
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,self.stacksContainer,name='draftingDialog')
    
    # ***********************************************************
    # define the methods for DraftingDialog    
    # ***********************************************************
    '''function genCardTbl
    input:     card stacks, a stack includes 2 cards
    process:   convert all stacks into visual stacks(a table widget) and place them in a group which only be selected one at a time
    return:    the generate Table(a widget)'''    
    def genCardTbl(self,stacks):
    # create a talbe(widget) to place all stack of cards
        tbl = gui.Table()
        self.group = gui.Group(value = None)
        # generate all cards included in the input argument stacks
        # and place them on the table
        print('The latest length of the stacks is ', len(stacks))
        card = [None]*len(stacks)
        vcard = [None]*len(stacks)
        for i in range(len(stacks)):
            # get the card information
            # create the image of each card as a table(widgit)
            card = stacks[i][0]
            vcard[i] = general.genVcard(card)
            # 4 cards in one row
            if (i % 4 == 0):
                tbl.tr()
                tbl.td(gui.Label('  '))
                tbl.tr()
            tbl.td(gui.Tool(self.group,vcard[i],value=i))
            tbl.td(gui.Label("    "))
            
        # monitor the event whether the selection change
        self.group.send(gui.CHANGE)
        def getGv(self):
            print(stacks[self.group.value][0].getName(), ' is selected')
            self._click.play()
        self.group.connect(gui.CHANGE,getGv,self)
        return tbl
    
    def paintStacks(self):
        self.stacksTbl = self.genCardTbl(self.stacks)
        self.stacksContainer.add(self.stacksTbl,50,10)
        
    def setStacks(self,stacks):
        self.stacks = stacks
        
    def setSelectedItem(self,Item):
        self._selectedItem = Item
    
    def getSelectedItem(self):
        return self._selectedItem
        
    def getConfirmButton(self):
        return self.confirmButton

'''a class to create a playing dialog for the human player
   In drarting phase, the selected cards will apper in this dialog
   In playing phase, the human player will select a card to play from this dialog'''        
class PlayingDialog(gui.Dialog):
    def __init__(self,cards,EsUsed,playerName):
        # 1. initialize
        self.cards = cards
        self.EsUsed = EsUsed
        self._playerName = playerName
        self.selectedItem = None
        # crate a group of cards for selection
        self.cardsGroup = gui.Group(value=None)
        # 2. load audios
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        
        # create the title of dialog
        lableStr = 'Playing Window for ' + self._playerName;
        title = gui.Label(lableStr)
        # create a container to show all unused cards ,confirm button and the Emergency stop card
        self.cardsContainer = gui.Container(width = 700, height = 150)
        self.cardsTbl = gui.Table()
        self.esCardButton = gui.Button() # it's an Emergency Stop card, just show it as a button
        
        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        def clsDialog(self):
            self.selectedItem = self.cardsGroup.value
            if len(self.cards) > 0 and self.selected:
                print('finally select ', self.cards[self.selectedItem].getName())
            elif len(self.cards) == 0:
                print('There is no card to play')
            elif not self.selected:
                print('you should select one card')
            self.selected = False
            self._confirm.play()
            
        self.confirmButton.connect(gui.CLICK,clsDialog,self)
        # add confirm button to container
        self.cardsContainer.add(self.confirmButton,380,120)
        
        # initialie Drafting dialog
        gui.Dialog.__init__(self,title,self.cardsContainer)
        
    # ********************************************************************    
    # define the methods for Playing Dialog    
    # ******************************************************************** 
    '''generate card group'''
    def genCardTbl(self,cards):
        # create a talbe(widget) to place all cards
        tbl = gui.Table(name = 'table')
        self.cardsGroup = gui.Group(value=None)
        # generate all cards included in the input argument stacks
        # and place them on the table
        amountCards = len(cards)
        if amountCards > 0:
            card = [None]*amountCards
            vcard = [None]*amountCards
            
            for i in range(amountCards):
                vcard[i] = general.genVcard(cards[i])
                tbl.td(gui.Tool(self.cardsGroup,vcard[i],value=i))
                tbl.td(gui.Spacer(width = 10, height = 20))
            # monitor the event whether the selection change
            self.selected = False
            self.cardsGroup.send(gui.CHANGE)
            def getGv(self):
                print(cards[self.cardsGroup.value].getName(), ' is selected')
                self.selected = True
                self._click.play()
            self.cardsGroup.connect(gui.CHANGE,getGv,self)
        return tbl
    
    '''update the cards area'''
    def paintCards(self,cards,EsUsed):    
        self.cards = cards
        self.EsUsed = EsUsed
        # remove the old widgets
        if self.cardsContainer.find('table'):
            self.cardsContainer.remove(self.cardsTbl)
        if self.cardsContainer.find('EsButton'):
            self.cardsContainer.remove(self.esCardButton)
        
        # generatge the new widgets
        # create a talbe(widget) to place all cards
        self.cardsTbl = self.genCardTbl(self.cards)
        # crate a button(widget) to place emergency stop card
        self.esCardButton = general.genEsCard(self.EsUsed)
        
        # add new widgets into the container
        self.cardsContainer.add(self.cardsTbl,10,10)
        self.cardsContainer.add(self.esCardButton,600,10)
        
    def getSelectedItem(self):
        return self.selectedItem
    
    def getConfirmButton(self):
        return self.confirmButton
    
    def setCards(self,cards):
        self.cards = cards
        
    def setEsUsed(self,EsUsed):
        self.EsUsed = EsUsed
        
'''Emergency Stop class, create the Emergency Stop Dialog '''
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
        EScontainer = gui.Container(width = 400, heigt = 300)
        # 2.1 create a label in container
        lable = gui.Label('Do you want to use Emergency Stop Card?')
        lbw,lbh = lable.resize()
        EScontainer.add(lable,int((400-lbw)/2),20)
        # 2.2 create a table with 'yes' or 'no' option in container and also a gruop for selection
        table = gui.Table()
        table.tr()
        g = gui.Group(value=0)
        table.td(gui.Tool(g,gui.Label('Yes'),value = 1))
        table.td(gui.Spacer(width = 50,height = 20))
        table.td(gui.Tool(g,gui.Label('No'),value = 0))
        tblw,tblh = table.resize()
        EScontainer.add(table,int((400-tblw)/2),20+lbh+20)
        g.send(gui.CHANGE)
        def gv(self):
            self._click.play()
        g.connect(gui.CHANGE,gv,self)
        
        # create a confirm button to confirm selection 
        self.confirmButton = gui.Button("Confirm")
        def cEsD(self):
            self.EsUsed = g.value
            print('ES WINDOW SELECTION IS ', self.EsUsed)
            self._confirm.play()
            self.close()
        self.confirmButton.connect(gui.CLICK,cEsD,self)
        
        # add confirm button to container
        EScontainer.add(self.confirmButton,160,100)
        # initialie Emergency Sop dialog
        gui.Dialog.__init__(self,title,EScontainer)
    
    def getEsUsed(self):
        return self.EsUsed
    
    def getConfirmButton(self):
        return self.confirmButton
        

'''revealCardsDialog class, display all played cards after all players have played their cards in the playing phase '''
class revealCardsDialog(gui.Dialog):
    def __init__(self):
        # initialize
        self.revealCards = []  # revealCards is a list of revealCard,revealCard = [playerName,Card]
        # 1. define the title of the dialog
        self.title = gui.Label('Reveal Cards Window')
        # 2. define the container of the dialog
        self.container = gui.Container(width = 400, heigt = 550) 
        
        # initialie Emergency Sop dialog
        gui.Dialog.__init__(self,self.title,self.container)
    
    def paintRevealedCard(self,revealCard):
        tbl = gui.Table()
        tbl.tr()
        # create the player name part as a button
        nameBlock = gui.Button(revealCard[0],width = 70,height = 25) 
        tbl.td(nameBlock)
        tbl.tr()
        tbl.td(gui.Spacer(width=1, height=5))
        tbl.tr()
        # create the card part as a table 
        g = gui.Group(value=None)
        cardBlock = general.genVcard(revealCard[1])
        tbl.td(gui.Tool(g,cardBlock,None))
        return tbl
    
    def paintRevealedCards(self,revealCards):
        self.container = gui.Container(width = 400, heigt = 300)
        x = 10
        cnt = 0
        for element in revealCards:
            if cnt < 4: # limit the maximum amount of revealed card to 4
                revealCardTbl = self.paintRevealedCard(element)
                self.container.add(revealCardTbl,x = x,y = 5)
                x += 100
            cnt += 1
        self.container.add(gui.Spacer(width = 100, height = 5), x = 0, y = 140)
        gui.Dialog.__init__(self,self.title,self.container)
        
    def getConfirmButton(self):
        return self.confirmButton
        



''' Define a humanPlayer class, which defines the whole GUI which will be used by a human player
    The HumanPlayer including follwing functions:
    1.  create a human player object with 2 arguments, 
            humanPlayer = humanPlayer(playerName,container)
                playerName is the Name of Player which will be shown in the title of all dialogs
                Container is the image container which will be used to display all windows in this container
    2.  open a drafting dialog in drafting phase, the human player can select a stack of cards in this dialog can press confirm
        button to confirm his/her selection.
            humanPlayer.DecisionMaking_Drafting(stacks)
                stacks is the input argument, all cards in the stacks will be shown in the drafting dialog
                
    3.  show/hide the playing dialog, since there are more than one players in the game, so, you may need this function to show/hide
        a specific player's playing dialog
            humanPlayer.showHidePlayDialog(show=1)
                show is the input argument with defaut value 1, 0: hide, 1: show
    
    4.  In the playing phase, when resolve for each player, the player many want to use Emergency Stop card, so a EsDialog is provided
        for human player to select whether use Emergency Stop
            humanPlayer.startEsDialog()
            
    5.  since the game manager should know when the human player finally confirms his selection and go to next turn
        So, the game manager can get the confirm button of 3 dialogs (drafting, playing and EmergencyStop)
            humanPlayer.getDraftDialogConfirmButton()
            humanPlayer.getPlayDialogConfirmButton()
            humanPlayer.getEsDialogConfirmButton()
'''
        
class humanPlayer():
    def __init__(self,playerName,container):
        # initialize parameter
        self.EsUsed = 0                 # whether Emergency Stop card is used, 0: not used, 1: used
        self.stacks = []                # stacks which will be displayed in drafting window
        self.playingCards = []          # current cards which hold by the player
        self.selectedCard = []          # the card played by the human player in this turn
        self.container = container      # the container
        self.playerName = playerName    # the name of player   
        self.ddx,self.ddy = 160,30      # the left top location of draft dialog
        self.pdx,self.pdy = 40,50       # the left top location of playing dialog
        self.esdx,self.esdy = 100,100   # the left top location of Emergency Stop dialog
        
        # *******************************************************
        # crate initial Drafting window without card 
        # *******************************************************
        self.draft_dialog = DraftingDialog(self.stacks,self.playerName)
        # when the human player press 'confirm' button to confirm his/her selection, then
        # 1. close the drafting dialog
        # 2. if the amount of remain cards in playing window is less than 4, then
        #    2.1 copy the cards from playing window
        #    2.2 append selected stack (2 cards) into cards set which will be shown in playing window
        #    2.3 re-build the playing window with new cards
        def ddq(self):
            if self.draft_dialog.getSelectedItem() != None:
                #self.container.remove(self.draft_dialog)
                self.draft_dialog.close()
                if len(self.play_dialog.cards) <= 4:
                    # append the selected cards in drafting window into playing window
                    self.playingCards.append(self.stacks[self.getSelectedStackIndex()][0])
                    self.playingCards.append(self.stacks[self.getSelectedStackIndex()][1])
                    print('the latest length of playingCards is ', len(self.playingCards))
                    # update the playing window with new cards
                    self.playDialogUpdate()
        ddConfirmButton = self.getDraftDialogConfirmButton()
        ddConfirmButton.connect(gui.CLICK,ddq,self)
        
        # *******************************************************
        # crate initial playing window without card 
        # *******************************************************
        self.play_dialog = PlayingDialog(self.playingCards,self.EsUsed,self.playerName)
        self.play_dialog.name = "playingDialog" + self.playerName
        self.container.add(self.play_dialog,self.pdx,self.pdy)
        def pdq(self):
            if self.play_dialog.getSelectedItem() is not None:
                self.selectedCard = self.playingCards[self.getSelectedCardIndex()]
                self.playingCards = general.delcard(self.playingCards,self.getSelectedCardIndex())
                print('the latest length of playingCards is ', len(self.playingCards))
                # update the playing window with new cards
                self.playDialogUpdate()
        pdConfirmButton = self.getPlayDialogConfirmButton()
        pdConfirmButton.connect(gui.CLICK,pdq,self)
        
        # *******************************************************
        # crate initial Emergency Stop window 
        # *******************************************************
        self.Es_Dialog =  EsDialog(self.playerName)
        def esq(self):
            #self.container.remove(self.Es_Dialog)
            self.EsUsed = self.getSelectedEs()
            # re-build the playing window with new cards
            self.playDialogUpdate()
        EsConfirmButton = self.getEsDialogConfirmButton()
        EsConfirmButton.connect(gui.CLICK,esq,self)
    
    # ***********************************************************
    # define methods for human player    
    # ***********************************************************
    def setStacks(self,stacks):
        self.stacks = stacks
        
    def setEsUsed(self,EsUsed):
        self.EsUsed = EsUsed
    
    def DecisionMaking_Drafting(self,stacks):
        self.stacks = stacks
        self.draft_dialog.setSelectedItem(Item = None)
        self.selectedStackIndex = None
        self.draft_dialog.setStacks(self.stacks)
        self.draft_dialog.paintStacks()
        #self.container.add(self.draft_dialog,self.ddx,self.ddy)
        self.draft_dialog.open()
    
    def playDialogUpdate(self):
        self.play_dialog.paintCards(self.playingCards,self.EsUsed)
        
    def showHidePlayDialog(self,show = True):
        if show and not self.container.find('playingDialog'+self.playerName):
            self.container.add(self.play_dialog,self.pdx,self.pdy)
            self.selectedCard = None
        elif not show and self.container.find('playingDialog'+self.playerName):
            self.container.remove(self.play_dialog)
    
    def startEsDialog(self):
        #self.container.add(self.Es_Dialog,self.esdx,self.esdy)
        self.Es_Dialog.open()
        
    def getSelectedStackIndex(self):
        return self.draft_dialog.getSelectedItem()
    
    def getSelectedCardIndex(self):
        return self.play_dialog.getSelectedItem()
    
    def getSelectedCard(self):
        return self.selectedCard
        
    def getSelectedEs(self):
        return self.Es_Dialog.getEsUsed()
    
    def getDraftDialogConfirmButton(self):
        return self.draft_dialog.getConfirmButton()
    
    def getPlayDialogConfirmButton(self):
        return self.play_dialog.getConfirmButton()
    
    def getEsDialogConfirmButton(self):
        return self.Es_Dialog.getConfirmButton()
    
    def getEsUsed(self):
        return self.EsUsed
        
# *********************************************************          
# Main
# ********************************************************* 
'''the class App is just an example showing how to use humanPlayer class'''
class App():
    def __init__(self,container):
        # initilize the gui
        #gui.Desktop.__init__(self)
        #self.connect(gui.QUIT,self.quit,None)
        
        # crate a container in APP
        #self.c = gui.Container(width=800,height=750)
        self.c = container
        
        # create a Deck
        deck = card.Deck()
        # reshuffle 2*3*playerAmount cards 
        playerAmount = 2;
        playerName_0 = 'Andy'
        playerName_1 = 'July'
        playerName_2 = 'Salary'
        playerName_3 = 'Alan'
        playerNames = [playerName_0,playerName_1,playerName_2,playerName_3]
        
        # -----------------------------------------------
        # step1. create a human player
        # -----------------------------------------------
        self.humanPlayer_0 = humanPlayer(playerName_0,self.c)
        self.humanPlayer_1 = humanPlayer(playerName_1,self.c)
        self.EsUsed = 0
        self.stacks = stacks = deck.createCardField(playerAmount)
    
        # -----------------------------------------------
        # create a button to open the drating dialog        
        # -----------------------------------------------
        b = gui.Button('Open Drafting Dialog')
        def ddo(self):
            self.humanPlayer_0.showHidePlayDialog(False)
            self.humanPlayer_1.showHidePlayDialog(False)
            self.humanPlayer_0.DecisionMaking_Drafting(self.stacks)
            # the game manager should monitor the confirm event from drafting dialog
        b.connect(gui.CLICK,ddo,self)
        self.c.add(b,300,10)
        
        def ddq_0(self):
            if self.humanPlayer_0.getSelectedStackIndex() is not None:
                self.stacks = general.delcard(self.stacks,self.humanPlayer_0.getSelectedStackIndex())
                print('draft dialog closed, the latest amount of stacks is ', len(self.stacks))
                self.humanPlayer_1.DecisionMaking_Drafting(self.stacks)
        self.hp0_ddcb = self.humanPlayer_0.getDraftDialogConfirmButton()
        self.hp0_ddcb.connect(gui.CLICK,ddq_0,self)
        
        def ddq_1(self):
            if self.humanPlayer_1.getSelectedStackIndex() is not None:
                self.stacks = general.delcard(self.stacks,self.humanPlayer_1.getSelectedStackIndex())
                print('draft dialog closed, the latest amount of stacks is ', len(self.stacks))
                if len(self.stacks) > 0:
                    self.humanPlayer_0.DecisionMaking_Drafting(self.stacks)
                else:
                    self.humanPlayer_0.showHidePlayDialog(True)
        self.hp1_ddcb = self.humanPlayer_1.getDraftDialogConfirmButton()
        self.hp1_ddcb.connect(gui.CLICK,ddq_1,self)
        
        # -----------------------------------------------
        # test  the function of open/close playing dialog
        # -----------------------------------------------
        self.openPlayingDialog = True
        buttonOCPD = gui.Button('Open/Close Playing Window')
        def ocpd(self):
            self.openPlayingDialog = not self.openPlayingDialog
            self.humanPlayer_0.showHidePlayDialog(self.openPlayingDialog)
            self.humanPlayer_1.showHidePlayDialog(not self.openPlayingDialog)
        buttonOCPD.connect(gui.CLICK,ocpd,self)
        self.c.add(buttonOCPD,50,10)
        
        # -----------------------------------------------
        # test to capture the confirmation of playing from human player
        # -----------------------------------------------
        self.player0_played = False
        self.player1_played = False
        self.revealedCards = []
        def pdq_0(self):
            if self.humanPlayer_0.getSelectedCard() is not None:
                self.player0_played = True
                self.revealedCards.append([playerName_0,self.humanPlayer_0.getSelectedCard()])
                cleanRevealedCards(self)
                self.humanPlayer_0.showHidePlayDialog(False)
                self.humanPlayer_1.showHidePlayDialog(True)
                if self.player0_played and self.player1_played:
                    self.player0_played = False
                    self.player1_played = False 
                    updateRevealedCards(self, self.revealedCards)
                    self.revealedCards = []
        self.hp0_pdcb = self.humanPlayer_0.getPlayDialogConfirmButton()
        self.hp0_pdcb.connect(gui.CLICK,pdq_0,self)
        
        def pdq_1(self):
            if self.humanPlayer_1.getSelectedCard() is not None:
                self.player1_played = True
                self.revealedCards.append([playerName_1,self.humanPlayer_1.getSelectedCard()])
                cleanRevealedCards(self)
                self.humanPlayer_1.showHidePlayDialog(False)
                self.humanPlayer_0.showHidePlayDialog(True)
                if self.player0_played and self.player1_played:
                    self.player0_played = False
                    self.player1_played = False 
                    updateRevealedCards(self, self.revealedCards)
                    self.revealedCards = []
        self.hp1_pdcb = self.humanPlayer_1.getPlayDialogConfirmButton()
        self.hp1_pdcb.connect(gui.CLICK,pdq_1,self)
        
        
        # -----------------------------------------------
        # create a button to test emergency stop card function
        # -----------------------------------------------
        bes = gui.Button('Open Emergency Stop Dialog')
        def eso(self):
            self.humanPlayer_0.startEsDialog()
            
        bes.connect(gui.CLICK,eso,self)
        self.c.add(bes,500,10)
        
        
        
        # -----------------------------------------------
        # test revealCardsDialog 
        # -----------------------------------------------
        # initilize a revealCardsDialog
        self.revealCardsDialog = revealCardsDialog()
        self.revealCardsDialog.name = 'revealCardsDialog'
        
        def updateRevealedCards(self,revealedCards):
            self.revealCardsDialog.paintRevealedCards(revealedCards)
            if self.c.find('revealCardsDialog'):
                self.c.remove(self.revealCardsDialog)
            self.c.add(self.revealCardsDialog,800,50)
        
        def cleanRevealedCards(self):
            self.revealCardsDialog.paintRevealedCards([])
            if self.c.find('revealCardsDialog'):
                self.c.remove(self.revealCardsDialog)
            self.c.add(self.revealCardsDialog,800,50)
        
        cleanRevealedCards(self)