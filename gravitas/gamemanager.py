"""Module containing the game manager class"""
from player import Player, Ship
from card import Card, Deck
import random

"""Game manager class. Home to all the game's logic."""
class GameManager:

    """Nested class enumerating recognized player types"""
    class PType:
        human = 0
        randAI = 1
    
    """Constructs the game manager. Takes a file pointer to a list of player
    configurations, creates the player and ship objects, hands over control of
    these to the player controllers, then starts the game loop."""
    def __init__(self, config):
        # Bookkeeping
        random.seed()
        self._turn = 0
        self._round = 0
        self._players = []
        self._deck = Deck()

        # Create the player objects
        availColors = [1,2,3,4]
        for p in self._parseConfig(config):
            c = random.choice(availColors)
            availColors.remove(c)
            player = Player(c, p[1])
            self._players.append(player)
            #TODO create and hand over player to player controller

        # Create NPC ships ("hulks")
        self._hulks = [Ship(pos=38)]
        if len(self._players) > 2:
            self._hulks.append(Ship(pos=28))

    """Helper function that reads the configuration file"""
    def _parseConfig(self, config):
        f = open(config, 'r')
        conflist = []
        for l in f:
            l = l.split()
            ptype = eval("GameManager.PType." + l[0])
            conflist.append((ptype, l[1]))
        f.close()
        return conflist

##### END OF ROOT LEVEL ########################################################
################################################################################
##### START OF ROUND LEVEL #####################################################

    """Sorts the players based on distance to the warp gate. If two or more
    players are in the singularity, their order is randomized."""
    def sortPlayers(self):
        # Pull all players in the singularity into a separate list
        inS = []
        for p in self._players:
            if p.getPos() == 0:
                inS.append(p)
                self._players.remove(p)

        # Shuffle the players in the singularity
        random.shuffle(inS)

        # Sort the remaining players
        self._players = sorted(self._players, key=lambda p: p.getDistanceToWG())

        # Concatenate
        self._players = self._players + inS

    """Starts the round; deals cards, prompts for selections, and starts the
    round loop"""
    def startRound(self):
        # Sort the players
        self.sortPlayers()

        # Reset all players Emergency Stop
        for p in self._players:
            p.resetES()

        # Prepare the field and start drawing
        field = self._deck.createCardField(len(self._players))
        for i in range(3):
            for p in self._players:
                #TODO prompt the players to draw a card
                # selection = p.promptForChoice(self._deck.percieveCardField())
                # self._deck.takeFromField(selection)
                field = self._deck.getField()
                print("Selection round " + str(i+1) + " for player " +
                      p.getName()) 
                #TODO either wait for the render loop to catch up or call it

##### END OF ROUND LEVEL #######################################################
################################################################################
##### START OF TURN LEVEL ######################################################

    """Turn loop function. Waits for all players to play cards, then triggers
    reveal and resolve"""
    def turn(self):
        # Prepares dictionary containing mappings of cards to players
        plays = {}
        
        # Polls all players for a card to play
        # while len(plays) < len(self._players):
            # for p in self._players:
                #TODO: Implement this functionality
                # card = p.pollPlay()
                # if card is not None:
                #     plays[card] = p
            #TODO: There should probably be a delay here so that the loop isn't
            # super fast
        
        # Reveal
        self.reveal(plays)

        # Resolve
        self.resolve(plays)


    """Turn reveal. Sends revealed cards to all player controllers"""
    def reveal(self, plays):
        cards = plays.keys()
        #TODO: keep track of player controllers
        # for pc in self._playerControllers:
        #     pc.sendReveal(cards)

    """Turn resolution. Given a list of cards, will sort and resolve plays"""
    def resolve(self, plays):
        # Get resolve-order sorted list of cards
        ordered = Deck.sortByResolution(plays)

        # Resolution loop
        for c in ordered:
            p = plays[c]

            # Determine if p is even capable of moving
            target = self._playerCanMove(p)
            if target is not None or c.getType == Card.Type.tractor:
                # Wait for Emergency Stop decision
                while True:
                    #TODO: implement this
                    useES = p.pollUseES()
                    if useES is not None:
                        break

            # Handle decision
            if not useES:
                self._resolvePlay(p, c, target)

    """Determines if the player is stuck or not. If the player is stuck, returns
    None, else returns the target ship (the one the player will travel towards)"""
    def _playerCanMove(self, player):
        # Set up the math
        nearestAhead = None
        nearestBehind = None
        distanceAhead = 100
        distanceBehind = 100
        numberAhead = 0
        numberBehind = 0

        # Loop over all ships on the board
        for s in (self._players + self._hulks):
            # Ignore the player being resolved
            if not s == player:
                # Ignore ships in the singularity
                if not s.getPos() == 0:
                    # The ship is behind the player
                    if player.directionTo(s) == -1:
                        numberBehind = numberBehind + 1
                        if player.distanceTo(s) < distanceBehind:
                            distanceBehind = player.distanceTo(s)
                            nearestBehind = s
                    # The ship is ahead of the player
                    else:
                        numberAhead = numberAhead + 1 
                        if player.distanceTo(s) < distanceAhead:
                            distanceAhead = player.distanceTo(s)
                            nearestAhead = s

        # Determine if the player can move
        if distanceAhead == distanceBehind:
            # Equidistant. Equal numbers?
            if numberAhead == numberBehind:
                # Stuck ship
                return None
            else:
                # Not stuck. Determine target
                if numberAhead > numberBehind:
                    return nearestAhead
                else:
                    return nearestBehind
        else:
            # There is a closest ship. Determine target.
            if distanceAhead < distanceBehind:
                return nearestAhead
            else:
                return nearestBehind
    
    """Resolves an individual play and moves the player accordingly"""
    def _resolvePlay(self, player, card, target):
        if card.getType() == Card.Type.normal:
            # Normal movement
            d = player.directionTo(target)
            player.move(card.getValue() * d)
            self._resolveCollission(player, d)
        elif card.getType() == Card.Type.repulsor:
            # Repulsor movement
            d = player.directionTo(target)
            player.move(card.getValue() * -d)
            self._resolveCollission(player, -d)
        else:
            # Tractor. Bastard
            # Build ship list
            ships = []
            for s in (self._players + self._hulks):
                if not s == player:
                    ships.append(s)

            # First sort (signed, since ships closer to the singularity get
            # priority in a tie)
            ships = sorted(ships, key=lambda s: (player.distanceTo(s) *
                                                 player.directionTo(s)))

            # Second sort (unsigned; preserves relative order due to stable
            # sort)
            ships = sorted(ships, key=lambda s: player.distanceTo(s))

            # Loop over sorted ships and resolve tractor
            for s in ships:
                d = s.directionTo(player)
                s.move(card.getValue() * d)
                self._resolveCollission(s, d)

    """Handles post-resolution placement so that no collissions occur"""
    def _resolveCollission(self, player, direction):
        # Loop until all collissions handled
        while True:
            # Disregard everything if the player is in the singularity
            if not player.getPos() == 0:
                collission = False
                for s in (self._players + self._hulks):
                    if not s == player:
                        if s.getPos() == player.getPos():
                            # Collission
                            collission = True
                            break
                if collission:
                    player.move(direction)
                else:
                    break
            else:
                break
