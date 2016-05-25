"""Module containing the game manager class"""
from player import Player, Ship
from card import Card, Deck
import random

class State:
    """The game state class. Beyond counters relating to the point in play, it
    also contains the reference to the deck and the lists of players (and
    hulks). The player list is a list of pairs (Player (or Ship) object,
    PlayerController (or None for hulks)). The State should be treated as
    read-only; only the Game Manger (and Factory) should write the state."""
    def __init__(self):
       # Bookkeeping
        self.turn = 0
        self.round = 0
        self.players = []
        self.hulks = []
        self.winner = None
        self.deck = Deck()
        self.GMState = 0

    def addHulk(self, position):
        self.hulks.append((Ship(pos=position), None))

    def addPlayer(self, player):
        self.players.append(player)

class GameManager:
    """Game manager class. Home to all the game's logic."""

    def __init__(self, state):
        """Constructs the game manager. Takes an already-constructed
        game-state."""
        self._state = state
        self._GMStates = {
            "init" : 0,
            "initdraft" : 1,
            "drafting" : 2,
            "initplay" : 3,
            "playing" : 4,
            "reveal" : 5,
            "resolve" : 6
        }

    #TODO make into a censored deep copy, the other players shouldn't know about
    # The controllers and shouldn't know which hands have already been played
    def copyState(self):
        #import copy
        #return copy.deepcopy(self._state)
        #YOLO
        return self._state

    """Function to update the game state. Only public function of the GM. Always
    returns a reference to the game state."""
    def update(self):
        if self._state.winner is None:
            if self._state.round < 6:
                if self._state.GMState == self._GMStates['init']:
                    # Initializes the round
                    self._initRound()
                elif self._state.GMState == self._GMStates['initdraft']:
                    # Prepare the draft
                    self._initDraft()
                elif self._state.GMState == self._GMStates['drafting']:
                    # Calls for drafting
                    self._draft()
                elif self._state.GMState == self._GMStates['initplay']:
                    # Prepare for play
                    self._initTurn()
                elif self._state.GMState == self._GMStates['playing']:
                    if self._state.turn < 6:
                        # Play game
                        self._turn()
                    else:
                        # End round
                        self._state.turn = 0
                        self._state.round += 1
                        self._state.GMState = self._GMStates['init']
                elif self._state.GMState == self._GMStates['reveal']:
                    # Reveal plays
                    self._reveal()
                elif self._state.GMState == self._GMStates['resolve']:
                    # Resolve plays; may set winner
                    self._resolve()
            else:
                # Figure out non-clear victory
                if self._state.winner is None:
                    self._sortPlayers()
                    self._state.winner = self._state.players[0][0]
        else:
            print("Got winner at round " + str(self._state.round) + ", turn " +
                  str(self._state.turn) + ": " + self._state.winner.getName())
        #TODO return true iff done (ie someone won), else return false
        return self._state

    def _initRound(self):
        """Initializes the round. Sorts the players, resets all Emergency Stops,
        readies a drafting field, and sets the state to drafting."""
        # Sort the players
        self._sortPlayers()
        # Reset all players Emergency Stop
        for p in self._state.players:
            p[0].resetEmergencyStop()
        # Sets the next state
        self._state.GMState = self._GMStates['initdraft']

    def _sortPlayers(self):
        """Sorts the players based on distance to the warp gate. If two or more
        players are in the singularity, their order is randomized."""
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

    def _initDraft(self):
        """Initializes the drafting step. Prepares the field and sets the
        drafting parameters."""
        self._field = self._state.deck.createCardField(len(self._state.players))
        self._draftsRemaining = 3
        self._draftPlayer = 0
        # Sets drafting
        self._state.GMState = self._GMStates['drafting']

    def _draft(self):
        """Updates the drafting step. Polls the next player in line for a
        choice. Updates the state to playing when all drafting is done."""
        player = self._state.players[self._draftPlayer]
        selection = player[1].pollDraft(self._state)
        
        # Handle draft
        if selection is not None:
            player[0].addCards(self._state.deck.takeFromField(selection))
            self._draftPlayer += 1
            if self._draftPlayer == len(self._state.players):
                self._draftsRemaining -= 1
                self._draftPlayer = 0

        # Check if draft is ended
        if self._draftsRemaining == 0:
            # End drafting
            self._state.GMState = self._GMStates['initplay']
                
    def _turn(self):
        """Turn update function. Polls a player to play."""
        # Gets the player to poll
        p = self._turnSelectPlayer()
        player = p[0]
        pc = p[1]
        # Get play
        play = pc.pollPlay(self._state)

        # Handle play
        if play is not None:
            self._plays[play] = p
            player.playCard(play)
            self._playersRemaining.remove(p)
        # Update state if neccessary
        if len(self._playersRemaining) == 0:
            self._state.GMState = self._GMStates['reveal']
        
    def _initTurn(self):
        """Turn initialization function. Prepares the plays dictionary, players
        remaining list."""
        # Prepares dictionary containing mappings of cards to players
        self._plays = {}
        # Prepares list of players which have yet to play
        self._playersRemaining = []
        for p in self._state.players:
            self._playersRemaining.append(p)
        # Sets the state to playing
        self._state.GMState = self._GMStates['playing']
        
    def _turnSelectPlayer(self):
        """Selects a random player to poll for play. Uses randomization since
        playing does not have to be in order."""
        return random.choice(self._playersRemaining)

    def _reveal(self):
        """Turn reveal. Sends revealed cards to all player controllers. Also
        prepares resolution."""
        # Informs all PCs
        cards = list(self._plays.keys())
        for p in self._state.players:
            p[1].informReveal(cards)

        # Prepares the resolution
        self._orderedPlays = Deck.sortByResolution(self._plays)
        self._toResolve = None

        # Updates state
        self._state.GMState = self._GMStates['resolve']

    def _initNextResolve(self):
        """Prepares the next play to be resolved."""
        if len(self._orderedPlays) > 0:
            firstCard = self._orderedPlays.pop(0)
            self._toResolve = (firstCard, self._plays[firstCard])
            

    def _resolve(self):
        """Turn resolution. Attempts to resolve the first card in the ordered
        play list. Will poll (applicable) players to use the Emergency Stop. Can
        also set the game winner if applicable."""
        # Check if there is a play to resolve
        if self._toResolve is None:
            # Bind the first card to be resolved
            self._initNextResolve()
        
        # Check again; if this fails, resolution is all done
        if self._toResolve is not None:
            # Bind the relevant variables
            card = self._toResolve[0]
            player = self._toResolve[1][0]
            pc = self._toResolve[1][1]
            resolved = False
            
            # Determine if the player can move
            target = self._playerCanMove(player)
            if target is not None or card.getType() == Card.Type.tractor:
                # Player can move. Test if Emergency Stop is available
                if player.canEmergencyStop():
                    # Player is able; poll
                    useEmergencyStop = pc.pollEmergencyStop(self._state)
                else:
                    # Player is unable
                    useEmergencyStop = False

                # Test if a decision was made
                if useEmergencyStop is not None:
                    # Execute resolution
                    if not useEmergencyStop:
                        self._resolvePlay(player, card, target)
                    else:
                        player.useEmergencyStop()
                    resolved = True

            if resolved:
                # Check for winner
                if player.distanceToFinish() == 0:
                    self._state.winner = self._toResolve

                # Clear the play
                self._toResolve = None
        else:
            # Set the state to next play and tick the turn counter
            self._state.GMState = self._GMStates['initplay']
            self._state.turn += 1

    def _playerCanMove(self, player):
        """Determines if the player is stuck or not. If the player is stuck,
        returns None, else returns the target ship (the one the player will
        travel towards)"""
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
    
    def _resolvePlay(self, player, card, target):
        """Resolves an individual play and moves the player accordingly"""
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

    def _resolveCollission(self, player, direction):
        """Handles post-resolution placement so that no collissions occur"""
        # Loop until all collissions handled
        while True:
            # Disregard everything if the player is in the singularity
            if not player.getPos() == 0:
                collission = False
                for ship in (self._state.players + self._state.hulks):
                    s = ship[0]
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
