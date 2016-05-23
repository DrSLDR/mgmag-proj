"""Module containing the game manager class"""
from player import Player, Ship
from card import Card, Deck
import random

"""The game state class. Beyond counters relating to the point in play, it also
contains the reference to the deck and the lists of players (and hulks). The
player list is a list of pairs (Player (or Ship) object, PlayerController (or
None for hulks)). The State should be treated as read-only; only the Game Manger
(and Factory) should write the state."""
class State:
    def __init__(self):
        # Bookkeeping
        self.turn = 0
        self.round = 0
        self.players = []
        self.hulks = []
        self.winner = None
        self.deck = Deck()

    def addHulk(self, position):
        self.hulks.append((Ship(pos=position), None))

    def addPlayer(self, player):
        self.players.append(player)


"""Game manager class. Home to all the game's logic."""
class GameManager:

    """Constructs the game manager. Takes a file pointer to a list of player
    configurations, creates the player and ship objects, hands over control of
    these to the player controllers, then starts the game loop."""
    def __init__(self, state):
        self._state = state

##### END OF ROOT LEVEL ########################################################
################################################################################
##### START OF GAME LEVEL ######################################################

    """The function to update the game state. """
    def update(self):
        if self._state.winner is None:
            self.game()

    """Main game loop. Runs the game for six rounds or until someone wins."""
    def game(self):
        while self._state.round < 6:
            self._state.round += 1
            if self.round():
                break

        # Figure out non-clear victory
        if self._state.winner is None:
            self.sortPlayers()
            self._state.winner = self._state.players[0][0]

        print("Got winner at round " + str(self._state.round) + ", turn " +
              str(self._state.turn) + ": " + self._state.winner.getName())


##### END OF GAME LEVEL ########################################################
################################################################################
##### START OF ROUND LEVEL #####################################################

    """Round loop function. Prepares a round, then runs six turns. Returns True
    immediately if a player has won, else False"""
    def round(self):
        self.startRound()
        self._state.turn = 0
        while self._state.turn < 6:
            self._state.turn += 1
            if self.turn():
                return True
        return False

    """Sorts the players based on distance to the warp gate. If two or more
    players are in the singularity, their order is randomized."""
    def sortPlayers(self):
        # Pull all players in the singularity into a separate list
        inS = []
        for p in self._state.players:
            if p[0].getPos() == 0:
                inS.append(p)
                self._state.players.remove(p)

        # Shuffle the players in the singularity
        random.shuffle(inS)

        # Sort the remaining players
        self._state.players = sorted(self._state.players, key=lambda p:
                                     p[0].distanceToFinish())

        # Concatenate
        self._state.players += inS

        # Reverse
        self._state.players.reverse()

    """Starts the round; deals cards, prompts for selections, and starts the
    round loop"""
    def startRound(self):
        # Sort the players
        self.sortPlayers()

        # Reset all players Emergency Stop
        for p in self._state.players:
            p[0].resetES()

        # Prepare the field and start drawing
        field = self._state.deck.createCardField(len(self._state.players))
        for i in range(3):
            for p in self._state.players:
                print("Selection round "+str(self._state.round)+"." + str(i+1) + 
                      " for player " + p[0].getName()) 
                #TODO prompt the players to draw a card
                selection = p[1].pollDraw(self._state.deck.percieveCardField())
                self._state.deck.takeFromField(selection)
                field = self._state.deck.getField()
                
                #TODO either wait for the render loop to catch up or call it

##### END OF ROUND LEVEL #######################################################
################################################################################
##### START OF TURN LEVEL ######################################################

    """Turn loop function. Waits for all players to play cards, then triggers
    reveal and resolve. Returns True immediately if a player has won, else False
    at the end of turn"""
    def turn(self):
        # Prepares dictionary containing mappings of cards to players
        plays = {}
        
        # Polls all players for a card to play
        # while len(plays) < len(self._players):
            # for p in self._players:
                #TODO: Implement this functionality
                # card = p[1].pollPlay(p[0].getHand())
                # if card is not None:
                #     plays[card] = p
        
        # Reveal
        self.reveal(plays)

        # Resolve
        return self.resolve(plays)

    """Turn reveal. Sends revealed cards to all player controllers"""
    def reveal(self, plays):
        cards = plays.keys()
        # for p in self._players:
        #     p[1].sendReveal(cards)

    """Turn resolution. Given a list of cards, will sort and resolve
    plays. Returns True if a player has entered the Warp Gate, else False"""
    def resolve(self, plays):
        # Get resolve-order sorted list of cards
        ordered = Deck.sortByResolution(plays)

        # Resolution loop
        for c in ordered:
            ptup = plays[c]
            p = ptup[0]
            pc = ptup[1]

            # Determine if p is even capable of moving
            target = self._state.playerCanMove(p)
            if target is not None or c.getType == Card.Type.tractor:
                # Wait for Emergency Stop decision
                while True:
                    #TODO: implement this
                    useES = pc.pollUseES(p.canES())
                    if useES is not None:
                        break

            # Handle decision
            if not useES:
                self._resolvePlay(p, c, target)

            # Check if the player has won the game
            if p.distanceToFinish() == 0:
                self._state.winner = ptup
                return True
        return False

    """Determines if the player is stuck or not. If the player is stuck, returns
    None, else returns the target ship (the one the player will travel
    towards)""" 
    def _playerCanMove(self, player):
        # Set up the math
        nearestAhead = None
        nearestBehind = None
        distanceAhead = 100
        distanceBehind = 100
        numberAhead = 0
        numberBehind = 0

        # Loop over all ships on the board
        for ship in (self._state.players + self._state.hulks):
            s = ship[0]
            # Ignore the player being resolved
            if not s == player:
                # Ignore ships in the singularity
                if not s.getPos() == 0:
                    # The ship is behind the player
                    if player.directionTo(s) == -1:
                        numberBehind += 1
                        if player.distanceTo(s) < distanceBehind:
                            distanceBehind = player.distanceTo(s)
                            nearestBehind = s
                    # The ship is ahead of the player
                    else:
                        numberAhead += 1 
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
            for ship in (self._state.players + self._state.hulks):
                s = ship[0]
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
                for s in (self._state.players + self._state.hulks):
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
