"""Contains the 'widget' part of the GUI (think buttons dialogs etc)"""
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
    def __init__(self,player):
        ADialog.__init__(
            self,
            'Drafing Window for %s' % player.name,
            Size(800,150),
        )
        # create a group of stacks for selection
        self.group = gui.Group(value=None)
        # a container to show all available stacks of cards and confirm button
        self.stacksTbl = gui.Table()
        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        self._selectedItem = None
        # define the the things need to do before close the drafting window
        def onConfirm(self):
            if self.group.value is None:
                return
            # get the final selected item
            self._selectedItem = self.group.value
            # play the confirm audio
            self._confirm.play()
        self.confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(self.confirmButton,300,120)
        # initialie Drafting dialog

    def genCardTbl(self,stacks):
        '''convert all stacks into visual stacks(a table widget) 
        and place them in a group which only be selected one at a time
        input:     card stacks, a stack includes 2 cards
        return:    the generate Table(a widget)'''
        # create a talbe(widget) to place all stack of cards
        tbl = gui.Table(name = 'stacksTable')
        self.group = gui.Group(value = None)
        # generate all cards included in the input argument stacks
        # and place them on the table
        card = [None]*len(stacks)
        vcard = [None]*len(stacks)
        for i in range(len(stacks)):
            # get the card information
            # create the image of each card as a table(widgit)
            card = stacks[i][1]
            vcard[i] = createCardView(card)
            tbl.td(gui.Tool(self.group,vcard[i],value=i))
            tbl.td(gui.Label("    "))
        # monitor the event whether the selection change
        self.group.send(gui.CHANGE)
        def getGv(self):
            self._click.play()
        self.group.connect(gui.CHANGE,getGv,self)
        return tbl

    def paintStacks(self,stacks):
        self._selectedItem = None
        if self.getContainer().find('stacksTable'):
            self.getContainer().remove(self.stacksTbl)
        self.stacksTbl = self.genCardTbl(stacks)
        self.getContainer().add(self.stacksTbl,30,10)
        
    def getSelectedItem(self):
        return self._selectedItem

class PlayingDialog(ADialog):
    '''this class creates a playing dialog for the human player
    In drarting phase, the selected cards will apper in this dialog
    In playing phase, the human player will select a card to play from this dialog'''

    def __init__(self,player):
        ADialog.__init__(
            self,
            'Playing Window for %s' % player.name,
            Size(700,150),
        )
        self.cards = [] 
        self.EsUsed = []
        self.selectedItem = None
        self.confirmed = False
        # crate a group of cards for selection
        self.cardsGroup = gui.Group(value=None)

        self.cardsTbl = gui.Table()
        self.esCardButton = gui.Button() # it's an Emergency Stop card, just show it as a button

        # create a confirm button for the human player to confirm his/her selection
        self.confirmButton = gui.Button("Confirm")
        def onConfirm(self):
            if self.cardsGroup.value is not None:
                self.selectedItem = self.cardsGroup.value
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
            self.cardsGroup.send(gui.CHANGE)
            def getGv(self):
                self._click.play()
            self.cardsGroup.connect(gui.CHANGE,getGv,self)
        return tbl

    def paintCards(self,cards,EsUsed):
        '''update the cards area'''
        self.cards = cards
        self.EsUsed = EsUsed
        self.selectedItem = None
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
        self.confirmed = False

    def getSelectedItem(self):
        return self.selectedItem
    
    def getSelectedCard(self):
        if self.selectedItem is not None:
            return self.cards[self.selectedItem]
        else:
            return None

class EmergencyStopDialog(ADialog):
    '''Emergency Stop class, create the Emergency Stop Dialog '''
    def __init__(self,player):
        ADialog.__init__(
            self,
            'Playing Window for %s' % player.name,
            Size(400,130),
        )
        self.EsUsed = 0
        self.confirmed = False
        # create a label in container
        lable = gui.Label('Do you want to use Emergency Stop Card?')
        lbw,lbh = lable.resize()
        self.getContainer().add(lable,int((400-lbw)/2),20)
        # 2.2 create a table with 'yes' or 'no' option in container
        # and also a gruop for selection
        table = gui.Table()
        table.tr()
        g = gui.Group(value=None)
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
            if g.value is not None:
                self.EsUsed = g.value
                self._confirm.play()
                g.value = None
        self.confirmButton.connect(gui.CLICK,cEsD,self)
        # add confirm button to container
        self.getContainer().add(self.confirmButton,160,100)
    
    def startEmergencyStopDialog(self):
        self.EsUsed = None
    
        
    def getEsUsed(self):
        return self.EsUsed


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
        ADialog.__init__(self,self.title,Size(width = 400, height = 150))

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
            HumanPlayer.DeciEmergencyStopDialog()
    '''
    def __init__(self, playerName,container):
        # initialize parameter
        self.stacks = []                # stacks which will be displayed in drafting window
        self.container = container 
        self.name = playerName    # the name of player
        self.isDraftDialogOpen = False
        self.isPlayDialogOpen = False
        self.isEmergencyStopDialogOpen = False

        # crate initial Drafting window without card
        self.draft_dialog = DraftingDialog(self)
        # create initial playing window without card
        self.play_dialog = PlayingDialog(self)
        # crate initial Emergency Stop window
        self.Es_Dialog =  EmergencyStopDialog(self)

    def decisionMaking_Drafting(self,stacks):
        self.stacks = stacks
        if self.isDraftDialogOpen is False:
            self.draft_dialog.paintStacks(self.stacks)
            self.container.add(self.draft_dialog,10,10)
            
        self.isDraftDialogOpen = True
        if self.draft_dialog.getSelectedItem() is not None:
            self.container.remove(self.draft_dialog)
            self.isDraftDialogOpen = False
            return self.draft_dialog.getSelectedItem()
        else:
            return None

    def decisionMaking_Playing(self,playingCards,EsUsed):
        if self.isPlayDialogOpen is False:
            self.play_dialog.paintCards(playingCards,EsUsed)
            self.container.add(self.play_dialog,10,10)
        self.isPlayDialogOpen = True
        if self.play_dialog.getSelectedItem() is not None:
            self.container.remove(self.play_dialog)
            self.isPlayDialogOpen = False
            return self.play_dialog.getSelectedCard()
        else:
            return None

    def decisionMaking_EmergencyStop(self):
        if self.isEmergencyStopDialogOpen is False:
            self.Es_Dialog.startEmergencyStopDialog()
            self.container.add(self.Es_Dialog,600,10)
        self.isEmergencyStopDialogOpen = True
        if self.Es_Dialog.getEsUsed() is not None:
            self.container.remove(self.Es_Dialog)
            self.isEmergencyStopDialogOpen = False    
            return self.Es_Dialog.getEsUsed()
        else:
            return None
