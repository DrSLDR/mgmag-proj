"""Contains the 'widget' part of the GUI (think buttons dialogs etc)"""
# This is not needed if you have PGU installed
import sys

import logging
import pygame
from pygame.locals import *
from pgu import gui

#import local libs
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
        super().__init__(
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
        super().__init__(
            'Drafing Window for %s' % player.name,
            Size(800,150),
        )
        # create a group of stacks for selection
        self._stacksGroup = gui.Group(name = 'stacksGroup',value=None)
        # a container to show all available stacks of cards and confirm button
        self._stacksTable = gui.Table()
        # create a confirm button for the human player to confirm his/her selection
        confirmButton = gui.Button("Confirm")
        self._selectedItem = None
        # define the the things need to do before close the drafting window
        def onConfirm(self):
            if self._stacksGroup.value is not None:
                # get the final selected item
                self._selectedItem = self._stacksGroup.value
                # remove all stacks from container
                self.getContainer().remove(self._stacksTable)
                # play the confirm audio
                self._confirm.play()
        confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(confirmButton,300,120)
        # initialie Drafting dialog

    def _genCardTbl(self,stacks):
        '''convert all stacks into visual stacks(a table widget) 
        and place them in a group which only be selected one at a time
        input:     card stacks, a stack includes 2 cards
        return:    the generate Table(a widget)'''
        # create a talbe(widget) to place all stack of cards
        self._stacksGroup = gui.Group(name = 'stacksGroup',value=None)
        stacksTable = gui.Table(name = 'stacksTable')
        # generate all cards included in the input argument stacks
        # and place them on the table
        card = [None]*len(stacks)
        vcard = [None]*len(stacks)
        for i in range(len(stacks)):
            # get the card information
            # create the image of each card as a table(widgit)
            card = stacks[i][1]
            vcard[i] = createCardView(card)
            stacksTable.td(gui.Tool(self._stacksGroup,vcard[i],value=i))
            stacksTable.td(gui.Label("    "))
        # monitor the event whether the selection change
        self._stacksGroup.send(gui.CHANGE)
        def onChange(self):
            self._click.play()
        self._stacksGroup.connect(gui.CHANGE,onChange,self)
        return stacksTable

    def paintStacks(self,stacks):
        self._selectedItem = None
        self._stacksTable = self._genCardTbl(stacks)
        self.getContainer().add(self._stacksTable,30,10)
        
    def getSelectedItem(self):
        return self._selectedItem

class PlayingDialog(ADialog):
    '''this class creates a playing dialog for the human player
    In drarting phase, the selected cards will apper in this dialog
    In playing phase, the human player will select a card to play from this dialog'''

    def __init__(self,player):
        super().__init__(
            'Playing Window for %s' % player.name,
            Size(700,150),
        )
        self._cards = [] 
        self._EsUsed = []
        self._selectedItem = None
        # crate a group of cards for selection
        self._cardsGroup = gui.Group(name='cardsGroup', value=None)
        self._cardsTable = gui.Table()
        self._esCardButton = gui.Button() # it's an Emergency Stop card, just show it as a button
        # create a confirm button for the human player to confirm his/her selection
        confirmButton = gui.Button("Confirm")
        def onConfirm(self):
            if self._cardsGroup.value is not None:
                self._selectedItem = self._cardsGroup.value
                self._confirm.play()
                self.getContainer().remove(self._cardsTable)
                self.getContainer().remove(self._esCardButton)
        confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(confirmButton,380,120)

    def _genCardTbl(self,cards):
        '''generate card group'''
        # create a talbe(widget) to place all cards
        cardsTable = gui.Table(name = 'cardsTable')
        self._cardsGroup = gui.Group(value=None)
        # generate all cards included in the input argument stacks
        # and place them on the table
        amountCards = len(cards)
        if amountCards > 0:
            card = [None]*amountCards
            vcard = [None]*amountCards
            for i in range(amountCards):
                vcard[i] = createCardView(cards[i])
                cardsTable.td(gui.Tool(self._cardsGroup,vcard[i],value=i))
                cardsTable.td(gui.Spacer(width = 10, height = 20))
            # monitor the event whether the selection change
            self._cardsGroup.send(gui.CHANGE)
            def onChange(self):
                self._click.play()
            self._cardsGroup.connect(gui.CHANGE,onChange,self)
        return cardsTable 

    def paintCards(self,cards,EsUsed):
        '''update the cards area'''
        self._cards = cards
        self._EsUsed = EsUsed
        self._selectedItem = None
        # generatge the new widgets
        # create a talbe(widget) to place all cards
        self._cardsTable = self._genCardTbl(self._cards)
        # crate a button(widget) to place emergency stop card
        self._esCardButton = createStopButton(self._EsUsed)

        # add new widgets into the container
        self.getContainer().add(self._cardsTable,10,10)
        self.getContainer().add(self._esCardButton,600,10)

    def getSelectedItem(self):
        return self._selectedItem
    
    def getSelectedCard(self):
        if self._selectedItem is not None:
            return self._cards[self._selectedItem]
        else:
            return None

class EmergencyStopDialog(ADialog):
    '''Emergency Stop class, create the Emergency Stop Dialog '''
    def __init__(self,player):
        super().__init__(
            'Playing Window for %s' % player.name,
            Size(400,130),
        )
        self._EsUsed = 0
        self._EmergencyStopTable = gui.Table()
        # create a label in container
        lable = gui.Label('Do you want to use Emergency Stop Card?')
        lableWidth,lableHeight = lable.resize()
        self.getContainer().add(lable,int((400-lableWidth)/2),20)
        self._group = gui.Group(name = 'YesNoGroup',value = None)

        # create a confirm button to confirm selection
        confirmButton = gui.Button("Confirm")
        def onConfirm(self):
            if self._group.value is not None:
                self._EsUsed = self._group.value
                self._confirm.play()
                self.getContainer().remove(self._EmergencyStopTable)
        confirmButton.connect(gui.CLICK,onConfirm,self)
        # add confirm button to container
        self.getContainer().add(confirmButton,160,100)
        
    def _genEmergencyStopTable(self):
        # create a table with 'yes' or 'no' option in container
        # and also a gruop for selection
        self._group = gui.Group(name = 'YesNoGroup',value = None)
        table = gui.Table()
        table.tr()
        table.td(gui.Tool(self._group,gui.Label('Yes'),value = 1))
        table.td(gui.Spacer(width = 50,height = 20))
        table.td(gui.Tool(self._group,gui.Label('No'),value = 0))
        self._group.send(gui.CHANGE)
        def onChange(self):
            self._click.play()
        self._group.connect(gui.CHANGE,onChange,self)
        return table
    
    def startEmergencyStopDialog(self):
        self._EsUsed = None
        self._EmergencyStopTable = self._genEmergencyStopTable()
        self.getContainer().add(self._EmergencyStopTable,130,60)
    
        
    def getEsUsed(self):
        return self._EsUsed


class RevealCardsDialog(ADialog):
    '''This class displays all played cards after the players have played 
    their cards in the playing phase '''
    def __init__(self):
        # revealCards is a list of revealCard,revealCard = [playerName,Card]
        self.revealCards = []
        self.title = 'Reveal Cards Window'
        self._repaint()

    def paintRevealedCards(self,revealCards):
        def paintRevealedCard(revealCard):
            table = gui.Table()
            table.tr()
            # create the player name part as a button
            nameBlock = gui.Button(revealCard[0],width = 70,height = 25)
            table = tbl.td(nameBlock)
            table = tbl.tr()
            table = tbl.td(gui.Spacer(width=1, height=5))
            table = tr()
            # create the card part as a table
            group = gui.Group(value=None)
            cardBlock = createCardView(revealCard[1])
            table.td(gui.Tool(group,cardBlock,None))
            return table 

        self._repaint()
        x = 10
        for element in revealCards:
            revealCardTbl = paintRevealedCard(element)
            self.getContainer().add(revealCardTbl,x = x,y = 5)
            x += 100
        self.getContainer().add(
            gui.Spacer(width = 100, height = 5), x = 0, y = 140
        )

    def _repaint(self):
        super().__init__(self.title,Size(width = 400, height = 150))

class HumanPlayer:
    ''' this class defines the GUI which will be used by a human player
        It includes the  following functions:
        1.  create a human player object with 2 arguments,
            HumanPlayer = HumanPlayer(playerName,container)
        2.  open a drafting dialog in drafting phase, the human player can 
            select a stack of cards in this dialog can press confirm
            button to confirm his/her selection.
            HumanPlayer.decisionMaking_Drafting(stacks)
            stacks is the input argument, all cards in the stacks will be shown 
            in the drafting dialog
        3.  open a playing dialog in playing phase, the human player can 
            select a card in this dialog can press confirm
            button to confirm his/her selection.
            HumanPlayer.decisionMaking_Playing(card,canEmergencyStop)
            stacks is the input argument, all cards in the stacks will be shown 
            in the drafting dialog
        4.  In the playing phase, when resolve for each player, the player 
            many want to use Emergency Stop card, so a EmergencyStopDialog is provided
            for human player to select whether use Emergency Stop
            HumanPlayer.decisionMaking_EmergencyStop()
    '''
    def __init__(self, playerName,container):
        # initialize parameter
        self._container = container 
        self.name = playerName    # the name of player
        self._isDraftDialogOpen = False
        self._isPlayDialogOpen = False
        self._isEmergencyStopDialogOpen = False

        # crate initial Drafting window
        self._draft_dialog = DraftingDialog(self)
        # create initial playing window
        self._play_dialog = PlayingDialog(self)
        # crate initial Emergency Stop window
        self._Es_Dialog =  EmergencyStopDialog(self)
        
    '''a function to open the drafting dialog if the dialog is not opened
       and close the dialog when human player confirm his selection'''
    def decisionMaking_Drafting(self,stacks):
        if self._isDraftDialogOpen is False:
            self._draft_dialog.paintStacks(stacks)
            self._container.add(self._draft_dialog,10,10)
            
        self._isDraftDialogOpen = True
        if self._draft_dialog.getSelectedItem() is not None:
            self._container.remove(self._draft_dialog)
            self._isDraftDialogOpen = False
            return self._draft_dialog.getSelectedItem()
        else:
            return None

    '''a function to open the playing dialog if the dialog is not opened, 
       and close the dialog when human player confirm his selection'''
    def decisionMaking_Playing(self,playingCards,canEmergencyStop):
        EsUsed = not canEmergencyStop
        if self._isPlayDialogOpen is False:
            self._play_dialog.paintCards(playingCards,EsUsed)
            self._container.add(self._play_dialog,10,10)
        self._isPlayDialogOpen = True
        if self._play_dialog.getSelectedItem() is not None:
            self._container.remove(self._play_dialog)
            self._isPlayDialogOpen = False
            return self._play_dialog.getSelectedCard()
        else:
            return None

    '''a function to open the Emergency Stop dialog if the dialog is not opened,
       and close the dialog when human player confirm his selection'''
    def decisionMaking_EmergencyStop(self):
        if self._isEmergencyStopDialogOpen is False:
            self._Es_Dialog.startEmergencyStopDialog()
            self._container.add(self._Es_Dialog,600,10)
        self._isEmergencyStopDialogOpen = True
        if self._Es_Dialog.getEsUsed() is not None:
            self._container.remove(self._Es_Dialog)
            self._isEmergencyStopDialogOpen = False    
            return self._Es_Dialog.getEsUsed()
        else:
            return None

class DrawingArea(gui.Widget):
    def __init__(self, width, height):
        gui.Widget.__init__(self, width=width, height=height)
        self.imageBuffer = pygame.Surface((width, height))
    def paint(self, surface):
        # Paint whatever has been captured in the buffer
        surface.blit(self.imageBuffer, (0, 0))
    # Call self function to take a snapshot of whatever has been rendered
    # onto the display over self widget.
    def save_background(self):
        display = pygame.displaylay.get_surface()
        self.imageBuffer.blit(display, self.get_abs_rect())

class MainGui(gui.Desktop):
    """It describes all the buttons and stuff like that. This is
    where pgu comes in,"""
    gameAreaHeight = 500
    gameArea = None
    menuArea = None

    def __init__(self, screen):
        self.gameManager = None # required, but dependency cycle
        self.log = logging.getLogger(type(self).__name__)
        super().__init__()

        container = gui.Container()
        # Setup the 'game' area where the action takes place
        self.gameArea = DrawingArea(screen.get_width(),
                                    self.gameAreaHeight)
        # Setup the gui area
        self.menuArea = gui.Container(width = screen.get_width(),
            height=screen.get_height()-self.gameAreaHeight)
        tabel = gui.Table(height=screen.get_height())
        tabel.tr()
        tabel.td(self.gameArea)
        tabel.tr()
        tabel.td(self.menuArea)
        container.add(tabel,0,0)
        self.init(container, screen)

        # create board
        self.log.debug("Creating game board")
        Size = namedtuple('Size', ['width', 'height'])

        from board import Renderer
        self.boardFunction = Renderer(Size(
            self.gameArea.rect.width,
            self.gameArea.rect.height
        )).render # a function

        self.log.debug("Creating font")
        self.font = pygame.font.SysFont("", 16)

    def get_render_area(self):
        return self.gameArea.get_abs_rect()
    def getHumanPlayerGuiContainer(self):
        return self.menuArea
    def handleEvents(self):
        # Process events
        self.log.debug("Handling event queue")
        for ev in pygame.event.get():
            self.log.debug("Handling event %s", ev)
            if (ev.type == pygame.QUIT or 
                ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                self.log.info("Caught exit action. Quitting.")
                logging.shutdown()
                exit() # that's a way to end the game I guess
            # Pass the event off to pgu
            self.event(ev)


    def render(self):
        # Render the game
        self.log.debug("Rendering game")
        rect = self.get_render_area()
        updates = []
        self.screen.set_clip(rect)
        temp = self.renderBoard(rect)
        if (temp):
            updates += temp
        self.screen.set_clip()
        self.log.debug("The screen is %s", self.screen)
        # Give pgu a chance to update the display
        temp = self.update()
        if (temp):
            updates += temp
        pygame.display.update(updates)

    def renderBoard(self, rect):
        """shows to a player what's going on"""
        backgroundColor = 0, 0, 255 # which is blue
        self.screen.fill(backgroundColor)
        def font(text, position, color=(255,255,255)):
            tmp = self.font.render(text, True, color)
            self.screen.blit(tmp, position)
        self.boardFunction(font, self.screen, self.gameManager.copyState(), 
            self.gameManager.getHuman(), # to draw the hand of the human user
            self.gameManager.getPlayedCards()) # to draw the revealed cards
        return (rect,)

class ScreenRenderer:
    def __init__(self, window):
        self.window = window
    def update(self):
        self.window.log.debug("rending pgu")
        self.window.handleEvents()
        self.window.render()

class FrameRateThrottler:
    def __init__(self, gameManger, gameEngine):
        self.gameManger = gameManger
        self.gameEngine = gameEngine
        self.log = logging.getLogger(type(self).__name__)

    def update(self):
        # Cap speed
        self.log.debug("Retrieving state")
        state = self.gameManager.copyState()

        fps = 0
        if state.GMState >= self.gameManager.GMStates['reveal']:
            fps = self._reducedFPS
            self.log.debug("Running at reduced (%i fps) speed", fps)
        else:
            fps = self._standardFPS
            self.log.debug("Normal (%i fps) loop speed", fps)
        self.gameEngine.framerateTrottle
