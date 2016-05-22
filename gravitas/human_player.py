#!/usr/bin/env python

# This is not needed if you have PGU installed
import sys

import pygame
from pygame.locals import *
from pgu import gui

#import local libs
import card
import strings

# define globle parameters
class params:
    FACE_UP = 0
    FACE_DOWN = 1

def createCardView(card):
    '''a function to generate a Visual card with a widget(Table)'''
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
    result = gui.Table(width = 30)
    result.add(gui.Label(' '))
    result.tr()
    result.add(gui.Label(' '))
    result.add(gui.Label(cardValue))
    result.tr()
    result.add(gui.Label(' '))
    result.add(gui.Label(cardName))
    result.tr()
    result.add(gui.Label(' '))
    result.add(gui.Label(cardTypeStr))
    result.tr()
    result.add(gui.Label(' '))
    return result

def createStopButton(face_sta):
    '''
    a function to generate visual Emergency Stop card return as a button
    '''
    return gui.Button(
        "ES Card" if face_sta == params.FACE_UP else " ",
        width = 75,
        height = 95,
        name = 'EsButton'
    )

from collections import namedtuple
Size=namedtuple('Size',['width','height'])

class ADialog(gui.Dialog):
    def __init__(self, title, containerSize):
        self._container = gui.Container(width = containerSize.width, height = containerSize.height)
        # Cause we want sound
        pygame.mixer.init()
        self._click = pygame.mixer.Sound(strings.Audio.click)
        self._confirm = pygame.mixer.Sound(strings.Audio.confirm)
        gui.Dialog.__init__(
            self,
            gui.Label(title),
            self._container,
            namea=title
        )
    def getContainer(self):
        return self._container

class DraftingDialog(ADialog):
    '''This dialog allows a human player to select cards from a set of stacks
    All stacks of cards are shown in the dialog, 
    human player can select one of the stacks of cards,
    and then press confirm button to confirm the selection'''
    def __init__(self,stacks,player):
        ADialog.__init__(
            self,
            'Drafing Window for %s' % player.name,
            Size(500,400),
        )
        self.stacks = stacks
        # create a group of stacks for selection
        self.group = gui.Group(value=None)
        # a container to show all available stacks of cards and confirm button
        self.stacksTbl = gui.Table()
        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        # define the the things need to do before close the drafting window
        def onConfirm(self):
            # get the final selected item
            self._selectedItem = self.group.value
            # play the confirm audio
            self._confirm.play()
            if self._selectedItem is not None:
                self.getContainer().remove(self.stacksTbl)
                self.close()
        self.confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(self.confirmButton,300,370)
        # initialie Drafting dialog

    def genCardTbl(self,stacks):
        '''convert all stacks into visual stacks(a table widget) 
        and place them in a group which only be selected one at a time
        input:     card stacks, a stack includes 2 cards
        return:    the generate Table(a widget)'''
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
            vcard[i] = createCardView(card)
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
        self.getContainer().add(self.stacksTbl,50,10)
    def setStacks(self,stacks):
        self.stacks = stacks
    def setSelectedItem(self,Item):
        self._selectedItem = Item
    def getSelectedItem(self):
        return self._selectedItem
    def getConfirmButton(self):
        return self.confirmButton

class PlayingDialog(ADialog):
    '''this class creates a playing dialog for the human player
    In drarting phase, the selected cards will apper in this dialog
    In playing phase, the human player will select a card to play from this dialog'''

    def __init__(self,cards,EsUsed,player):
        ADialog.__init__(
            self,
            'Playing Window for %s' % player.name,
            Size(700,150),
        )
        self.cards = cards
        self.EsUsed = EsUsed
        self.selectedItem = None
        # crate a group of cards for selection
        self.cardsGroup = gui.Group(value=None)

        self.cardsTbl = gui.Table()
        self.esCardButton = gui.Button() # it's an Emergency Stop card, just show it as a button

        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        def onConfirm(self):
            self.selectedItem = self.cardsGroup.value
            if len(self.cards) > 0 and self.selected:
                print('finally select ', self.cards[self.selectedItem].getName())
            elif len(self.cards) == 0:
                print('There is no card to play')
            elif not self.selected:
                print('you should select one card')
            self.selected = False
            self._confirm.play()

        self.confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(self.confirmButton,380,120)

    def genCardTbl(self,cards):
        '''generate card group'''
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
                vcard[i] = createCardView(cards[i])
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

    def paintCards(self,cards,EsUsed):
        '''update the cards area'''
        self.cards = cards
        self.EsUsed = EsUsed
        # remove the old widgets
        if self.getContainer().find('table'):
            self.getContainer().remove(self.cardsTbl)
        if self.getContainer().find('EsButton'):
            self.getContainer().remove(self.esCardButton)

        # generatge the new widgets
        # create a talbe(widget) to place all cards
        self.cardsTbl = self.genCardTbl(self.cards)
        # crate a button(widget) to place emergency stop card
        self.esCardButton = createStopButton(self.EsUsed)

        # add new widgets into the container
        self.getContainer().add(self.cardsTbl,10,10)
        self.getContainer().add(self.esCardButton,600,10)

    def getSelectedItem(self):
        return self.selectedItem
    def getConfirmButton(self):
        return self.confirmButton
    def setCards(self,cards):
        self.cards = cards
    def setEsUsed(self,EsUsed):
        self.EsUsed = EsUsed

class EmergencyStopDialog(ADialog):
    '''Emergency Stop class, create the Emergency Stop Dialog '''
    def __init__(self,player):
        ADialog.__init__(
            self,
            'Playing Window for %s' % player.name,
            Size(400,300),
        )
        self.EsUsed = 0
        # create a label in container
        lable = gui.Label('Do you want to use Emergency Stop Card?')
        lbw,lbh = lable.resize()
        self.getContainer().add(lable,int((400-lbw)/2),20)
        # 2.2 create a table with 'yes' or 'no' option in container
        # and also a gruop for selection
        table = gui.Table()
        table.tr()
        g = gui.Group(value=0)
        table.td(gui.Tool(g,gui.Label('Yes'),value = 1))
        table.td(gui.Spacer(width = 50,height = 20))
        table.td(gui.Tool(g,gui.Label('No'),value = 0))
        tblw,tblh = table.resize()
        self.getContainer().add(table,int((400-tblw)/2),20+lbh+20)
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
        self.getContainer().add(self.confirmButton,160,100)

    def getEsUsed(self):
        return self.EsUsed

    def getConfirmButton(self):
        return self.confirmButton


class RevealCardsDialog(ADialog):
    '''This class displays all played cards after the players have played 
    their cards in the playing phase '''
    def __init__(self):
        # revealCards is a list of revealCard,revealCard = [playerName,Card]
        self.revealCards = []
        self.title = 'Reveal Cards Window'
        self.repaint()

    def paintRevealedCards(self,revealCards):
        def paintRevealedCard(revealCard):
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
            cardBlock = createCardView(revealCard[1])
            tbl.td(gui.Tool(g,cardBlock,None))
            return tbl

        self.repaint()
        x = 10
        for element in revealCards:
            revealCardTbl = paintRevealedCard(element)
            self.getContainer().add(revealCardTbl,x = x,y = 5)
            x += 100
        self.getContainer().add(
            gui.Spacer(width = 100, height = 5), x = 0, y = 140
        )

    def repaint(self):
        ADialog.__init__(self,self.title,Size(width = 400, height = 300))

    def getConfirmButton(self):
        return self.confirmButton

class HumanPlayer():
    ''' this class defines the GUI which will be used by a human player
        It includes the  following functions:
        1.  create a human player object with 2 arguments,
            HumanPlayer = HumanPlayer(playerName,container)
            playerName is the Name of Player which will be shown in 
            the title of all dialogs. Container is the image container 
            which will be used to display all windows in this container
        2.  open a drafting dialog in drafting phase, the human player can 
            select a stack of cards in this dialog can press confirm
            button to confirm his/her selection.
            HumanPlayer.DecisionMaking_Drafting(stacks)
            stacks is the input argument, all cards in the stacks will be shown 
            in the drafting dialog
        3.  show/hide the playing dialog, since there are more than one 
            players in the game, so, you may need this function to show/hide
            a specific player's playing dialog
            HumanPlayer.showHidePlayDialog(show=1)
            show is the input argument with defaut value 1, 0: hide, 1: show
        4.  In the playing phase, when resolve for each player, the player 
            many want to use Emergency Stop card, so a EmergencyStopDialog is provided
            for human player to select whether use Emergency Stop
            HumanPlayer.startEmergencyStopDialog()
        5.  since the game manager should know when the human player finally 
            confirms his selection and go to next turn
            So, the game manager can get the confirm button of 3 dialogs 
            (drafting, playing and EmergencyStop)
                HumanPlayer.getDraftDialogConfirmButton()
                HumanPlayer.getPlayDialogConfirmButton()
                HumanPlayer.getEmergencyStopDialogConfirmButton()
    '''
    def __init__(self, playerName,container):
        # initialize parameter
        self.EsUsed = 0                 # whether Emergency Stop card is used, 0: not used, 1: used
        self.stacks = []                # stacks which will be displayed in drafting window
        self.playingCards = []          # current cards which hold by the player
        self.selectedCard = []          # the card played by the human player in this turn
        self.container = container      
        self.name = playerName    # the name of player
        self.ddx,self.ddy = 160,30      # the left top location of draft dialog
        self.pdx,self.pdy = 40,50       # the left top location of playing dialog
        self.esdx,self.esdy = 100,100   # the left top location of Emergency Stop dialog

        # crate initial Drafting window without card
        self.draft_dialog = DraftingDialog(self.stacks,self)
        # when the human player press 'confirm' button to confirm his/her selection, then
        # 1. close the drafting dialog
        # 2. if the amount of remain cards in playing window is less than 4, then
        #    2.1 copy the cards from playing window
        #    2.2 append selected stack (2 cards) into cards set which will be shown in playing window
        #    2.3 re-build the playing window with new cards
        def ddq(self):
            if self.draft_dialog.getSelectedItem() == None:
                return
            #self.container.remove(self.draft_dialog)
            self.draft_dialog.close()
            if len(self.play_dialog.cards) > 4:
                return
            # append the selected cards in drafting window into playing window
            self.playingCards.append(self.stacks[self.getSelectedStackIndex()][0])
            self.playingCards.append(self.stacks[self.getSelectedStackIndex()][1])
            print('the latest length of playingCards is ', len(self.playingCards))
            # update the playing window with new cards
            self.playDialogUpdate()
        ddConfirmButton = self.getDraftDialogConfirmButton()
        ddConfirmButton.connect(gui.CLICK,ddq,self)

        # create initial playing window without card
        self.play_dialog = PlayingDialog(self.playingCards,self.EsUsed,self)
        self.play_dialog.name = "playingDialog" + self.name
        self.container.add(self.play_dialog,self.pdx,self.pdy)
        def pdq(self):
            if self.play_dialog.getSelectedItem() is not None:
                self.selectedCard = self.playingCards[self.getSelectedCardIndex()]
                self.playingCards.pop(self.getSelectedCardIndex())
                print('the latest length of playingCards is ', len(self.playingCards))
                # update the playing window with new cards
                self.playDialogUpdate()
        pdConfirmButton = self.getPlayDialogConfirmButton()
        pdConfirmButton.connect(gui.CLICK,pdq,self)

        # crate initial Emergency Stop window
        self.Es_Dialog =  EmergencyStopDialog(self)
        def esq(self):
            #self.container.remove(self.Es_Dialog)
            self.EsUsed = self.getSelectedEs()
            # re-build the playing window with new cards
            self.playDialogUpdate()
        EsConfirmButton = self.getEmergencyStopDialogConfirmButton()
        EsConfirmButton.connect(gui.CLICK,esq,self)

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
        self.draft_dialog.open()

    def playDialogUpdate(self):
        self.play_dialog.paintCards(self.playingCards,self.EsUsed)

    def showHidePlayDialog(self,show = True):
        if show and not self.container.find('playingDialog'+self.name):
            self.container.add(self.play_dialog,self.pdx,self.pdy)
            self.selectedCard = None
        elif not show and self.container.find('playingDialog'+self.name):
            self.container.remove(self.play_dialog)

    def startEmergencyStopDialog(self):
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

    def getEmergencyStopDialogConfirmButton(self):
        return self.Es_Dialog.getConfirmButton()

    def getEsUsed(self):
        return self.EsUsed


class App():
    '''the class App is just an example showing how to use HumanPlayer class'''
    def __init__(self,container):
        # create a Deck
        deck = card.Deck()
        playerAmount = 2;
        playerNames = ['Andy','July','Salary','Alan']

        # Create a human player
        self.humanPlayer_0 = HumanPlayer(playerNames[0],container)
        self.humanPlayer_1 = HumanPlayer(playerNames[1],container)
        self.stacks = deck.createCardField(playerAmount)

        # Create a button to open the drating dialog
        b = gui.Button('Open Drafting Dialog')
        def ddo(self):
            self.humanPlayer_0.showHidePlayDialog(False)
            self.humanPlayer_1.showHidePlayDialog(False)
            self.humanPlayer_0.DecisionMaking_Drafting(self.stacks)
            # the game manager should monitor the confirm event from drafting dialog
        b.connect(gui.CLICK,ddo,self)
        container.add(b,300,10)

        def ddq_0(self):
            if self.humanPlayer_0.getSelectedStackIndex() is not None:
                self.stacks.pop(self.humanPlayer_0.getSelectedStackIndex())
                print('draft dialog closed, the latest amount of stacks is ', len(self.stacks))
                self.humanPlayer_1.DecisionMaking_Drafting(self.stacks)
        self.hp0_ddcb = self.humanPlayer_0.getDraftDialogConfirmButton()
        self.hp0_ddcb.connect(gui.CLICK,ddq_0,self)

        def ddq_1(self):
            if self.humanPlayer_1.getSelectedStackIndex() is not None:
                self.stacks.pop(self.humanPlayer_1.getSelectedStackIndex())
                print('draft dialog closed, the latest amount of stacks is ', len(self.stacks))
                if len(self.stacks) > 0:
                    self.humanPlayer_0.DecisionMaking_Drafting(self.stacks)
                else:
                    self.humanPlayer_0.showHidePlayDialog(True)
        self.hp1_ddcb = self.humanPlayer_1.getDraftDialogConfirmButton()
        self.hp1_ddcb.connect(gui.CLICK,ddq_1,self)

        # test  the function of open/close playing dialog
        self.openPlayingDialog = True
        buttonOCPD = gui.Button('Open/Close Playing Window')
        def ocpd(self):
            self.openPlayingDialog = not self.openPlayingDialog
            self.humanPlayer_0.showHidePlayDialog(self.openPlayingDialog)
            self.humanPlayer_1.showHidePlayDialog(not self.openPlayingDialog)
        buttonOCPD.connect(gui.CLICK,ocpd,self)
        container.add(buttonOCPD,50,10)

        # test to capture the confirmation of playing from human player
        self.player0_played = False
        self.player1_played = False
        self.revealedCards = []
        def pdq_0(self):
            if self.humanPlayer_0.getSelectedCard() is not None:
                self.player0_played = True
                self.revealedCards.append([playerNames[0],self.humanPlayer_0.getSelectedCard()])
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
                self.revealedCards.append([playerNames[1],self.humanPlayer_1.getSelectedCard()])
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

        # create a button to test emergency stop card function
        bes = gui.Button('Open Emergency Stop Dialog')
        def eso(self):
            self.humanPlayer_0.startEmergencyStopDialog()

        bes.connect(gui.CLICK,eso,self)
        container.add(bes,500,10)

        # Test RevealCardsDialog
        # initilize a RevealCardsDialog
        self.revealCardsDialog = RevealCardsDialog()
        self.revealCardsDialog.name = 'revealCardsDialog'
        def updateRevealedCards(self,revealedCards):
            self.revealCardsDialog.paintRevealedCards(revealedCards)
            if container.find('RevealCardsDialog'):
                container.remove(self.revealCardsDialog)
            container.add(self.revealCardsDialog,800,50)
        def cleanRevealedCards(self):
            self.revealCardsDialog.paintRevealedCards([])
            if container.find('RevealCardsDialog'):
                container.remove(self.revealCardsDialog)
            container.add(self.revealCardsDialog,800,50)
        cleanRevealedCards(self)
