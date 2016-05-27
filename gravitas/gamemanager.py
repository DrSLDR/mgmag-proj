"""Module containing the game manager class"""
from model.player import Player
from model.ship import Ship
from model.card import Card, Deck
from controller.human import Human_PC
import random, logging, copy

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

    def getHumanPlayer(self):
        # finds the first (and hopefully only) human in between the players
        humans = [p for p in self.players if p[1] and p[1].isHuman()]
        if len(humans) == 0 :
            return None
        else:
            return humans[0][0]

class GameManager:
    """Game manager class. Home to all the game's logic."""

    def __init__(self, state):
        """Constructs the game manager. Takes an already-constructed
        game-state."""
        self._state = state
        self.log = logging.getLogger(__name__)
        self._GMStates = {
            "init" : 0,
            "initdraft" : 1,
            "drafting" : 2,
            "initplay" : 3,
            "playing" : 4,
            "reveal" : 5,
            "resolve" : 6
        }

    def copyState(self):
        """Returns a copy of the state"""
        self.log.debug("Inside %s", self.copyState.__name__)
        self.log.debug("Creating semi-shallow state copy")
        state = copy.copy(self._state)
        state.players = []
        self.log.debug("Creating censored list of players")
        for p in self._state.players:
            self.log.debug("Censoring %s", p[0])
            playerCopy = p[0].makeCensoredCopy()
            state.addPlayer((playerCopy, None))
            self.log.debug("Censored player tuple created and added to state")

        self.log.debug("Deepcopying hulks")
        hulks = copy.deepcopy(self._state.hulks)
        state.hulks = hulks

        self.log.debug("Deepcopying deck")
        state.deck = copy.deepcopy(self._state.deck)

        self.log.debug("Returning")
        return state

    def update(self):
        """Function to update the game state. Only public function of the
        GM. Returns True if a winner has been decided."""
        self.log.debug("Inside %s", self.update.__name__)
        if self._state.winner is None:
            self.log.debug("No known winner")
            if self._state.round < 6:
                self.log.info("Game is not over. In round %i",
                               self._state.round)
                if self._state.GMState == self._GMStates['init']:
                    # Initializes the round
                    self.log.info("Game is in init state")
                    self._initRound()
                elif self._state.GMState == self._GMStates['initdraft']:
                    # Prepare the draft
                    self.log.info("Game is in initdraft state")
                    self._initDraft()
                elif self._state.GMState == self._GMStates['drafting']:
                    # Calls for drafting
                    self.log.info("Game is in drafting state")
                    self._draft()
                elif self._state.GMState == self._GMStates['initplay']:
                    # Prepare for play
                    self.log.info("Game is in initplay state")
                    self._initTurn()
                elif self._state.GMState == self._GMStates['playing']:
                    self.log.info("Game is in playing state")
                    if self._state.turn < 6:
                        # Play game
                        self.log.info("Round is not over. At turn %i",
                                      self._state.turn)
                        self._turn()
                    else:
                        # End round
                        self.log.info("End of round %i", self._state.round)
                        self._state.turn = 0
                        self._state.round += 1
                        self._state.GMState = self._GMStates['init']
                elif self._state.GMState == self._GMStates['reveal']:
                    # Reveal plays
                    self.log.info("Game is in reveal state")
                    self._reveal()
                elif self._state.GMState == self._GMStates['resolve']:
                    # Resolve plays; may set winner
                    self.log.info("Game is in resolve state")
                    self._resolve()
            else:
                self.log.info("Game is over. Figuring out winner.")
                # Figure out non-clear victory
                if self._state.winner is None:
                    self._sortPlayers()
                    self._state.winner = self._state.players[0][0]
        else:
            self.log.info("Got winner at round %i, turn %i: %s",
                          self._state.round, self._state.turn,
                          self._state.winner.getName())
            return True

    def _initRound(self):
        """Initializes the round. Sorts the players, resets all Emergency Stops,
        readies a drafting field, and sets the state to drafting."""
        self.log.debug("Inside %s", self._initRound.__name__)
        # Sort the players
        self._sortPlayers()
        # Reset all players Emergency Stop
        for p in self._state.players:
            self.log.debug("Resetting Emergency Stop of player %s", p[0])
            p[0].resetEmergencyStop()
        # Sets the next state
        self.log.debug("Ticking game state to initdraft")
        self._state.GMState = self._GMStates['initdraft']

    def _sortPlayers(self):
        """Sorts the players based on distance to the warp gate. If two or more
        players are in the singularity, their order is randomized."""
        self.log.debug("Inside %s", self._sortPlayers.__name__)
        # Pull all players in the singularity into a separate list
        self.log.debug("Sorting out players in the Singularity")
        inS = []
        for p in self._state.players:
            self.log.debug("Handling player %s", p[0])
            if p[0].getPos() == 0:
                self.log.debug("Player is in the Singularity. Will be shuffled")
                inS.append(p)

        # Pull players in the singularity from the main player list
        self.log.debug("Pulling players from the player list")
        for p in inS:
            self.log.debug("Removing %s from the state player list", p[0])
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
        self.log.debug("Order of players is now %s", self._state.players)

    def _initDraft(self):
        """Initializes the drafting step. Prepares the field and sets the
        drafting parameters."""
        self.log.debug("Inside %s", self._initDraft.__name__)
        self._field = self._state.deck.createCardField(len(self._state.players))
        self.log.info("Generated fields %s", self._field)
        self._draftsRemaining = 3
        self._draftPlayer = 0
        # Sets drafting
        self.log.debug("Ticking state to drafting")
        self._state.GMState = self._GMStates['drafting']

    def _draft(self):
        """Updates the drafting step. Polls the next player in line for a
        choice. Updates the state to playing when all drafting is done."""
        self.log.debug("Inside %s", self._draft.__name__)
        player = self._state.players[self._draftPlayer]
        self.log.info("Polling %s to draft", player[0])
        selection = player[1].pollDraft(self.copyState())
        
        # Handle draft
        if selection is not None:
            self.log.debug("Got field index %i. Handling draft", selection)
            cards = self._state.deck.takeFromField(selection)
            self.log.info("%s drafted cards %s", player[0], cards)
            player[0].addCards(cards)
            self.log.debug("Hand of %s is now %s", player[0],
                           player[0].getHand()) 
            self._draftPlayer += 1
            if self._draftPlayer == len(self._state.players):
                self._draftsRemaining -= 1
                self._draftPlayer = 0

        # Check if draft is ended
        if self._draftsRemaining == 0:
            # End drafting
            self.log.debug("End of drafting. Ticking state to initplay")
            self._state.GMState = self._GMStates['initplay']
                
    def _turn(self):
        """Turn update function. Polls a player to play."""
        self.log.debug("Inside %s", self._turn.__name__)
        # Gets the player to poll
        p = self._turnSelectPlayer()
        player = p[0]
        pc = p[1]
        # Get play
        self.log.info("Polling %s to play", player)
        play = pc.pollPlay(self.copyState())

        # Handle play
        if play is not None:
            self.log.info("%s played %s", player, play)
            self._plays[play] = p
            player.playCard(play)
            self.log.debug("Plays are now %s", self._plays)
            self.log.debug("Hand of %s is now %s", player, player.getHand())
            self._playersRemaining.remove(p)
        # Update state if neccessary
        if len(self._playersRemaining) == 0:
            self._state.GMState = self._GMStates['reveal']
        
    def _initTurn(self):
        """Turn initialization function. Prepares the plays dictionary, players
        remaining list."""
        self.log.debug("Inside %s", self._initTurn.__name__)
        # Prepares dictionary containing mappings of cards to players
        self._plays = {}
        # Prepares list of players which have yet to play
        self._playersRemaining = []
        for p in self._state.players:
            self._playersRemaining.append(p)
        # Sets the state to playing
        self.log.debug("Ticking state to playing")
        self._state.GMState = self._GMStates['playing']
        
    def _turnSelectPlayer(self):
        """Selects a random player to poll for play. Uses randomization since
        playing does not have to be in order."""
        self.log.debug("Inside %s", self._turnSelectPlayer.__name__)
        self.log.debug("Remaining players are %s", self._playersRemaining)
        self.log.debug("%s returning", self._turnSelectPlayer.__name__)
        return random.choice(self._playersRemaining)

    def _reveal(self):
        """Turn reveal. Sends revealed cards to all player controllers. Also
        prepares resolution."""
        self.log.debug("Inside %s", self._reveal.__name__)        
        # Informs all PCs
        cards = list(self._plays.keys())
        for p in self._state.players:
            self.log.debug("Informing %s of plays", p[0])
            p[1].informReveal(cards)

        # Prepares the resolution
        self._orderedPlays = Deck.sortByResolution(self._plays)
        self.log.info("Order of resolution will be %s", self._orderedPlays)
        self._toResolve = None

        # Updates state
        self.log.debug("Ticking state to resolve")
        self._state.GMState = self._GMStates['resolve']

    def _initNextResolve(self):
        """Prepares the next play to be resolved."""
        self.log.debug("Inside %s", self._initNextResolve.__name__)
        if len(self._orderedPlays) > 0:
            firstCard = self._orderedPlays.pop(0)
            self._toResolve = (firstCard, self._plays[firstCard])
            self.log.debug("Next card to resolve is %s", firstCard)

    def _resolve(self):
        """Turn resolution. Attempts to resolve the first card in the ordered
        play list. Will poll (applicable) players to use the Emergency Stop. Can
        also set the game winner if applicable."""
        self.log.debug("Inside %s", self._resolve.__name__)
        # Check if there is a play to resolve
        if self._toResolve is None:
            self.log.debug("No next resolution is set")
            # Bind the first card to be resolved
            self._initNextResolve()
        
        # Check again; if this fails, resolution is all done
        if self._toResolve is not None:
            # Bind the relevant variables
            card = self._toResolve[0]
            player = self._toResolve[1][0]
            pc = self._toResolve[1][1]
            resolved = False
            self.log.debug("Attempting to resolve play %s by %s", card, player)
            
            # Determine if the player can move
            target = self._playerCanMove(player)
            if target is not None or card.getType() == Card.Type.tractor:
                # Player can move. Test if Emergency Stop is available
                self.log.debug("Player isn't stuck. Targeting %s. Resolution "+
                               "continues", target)
                if player.canEmergencyStop():
                    # Player is able; poll
                    self.log.info("Polling %s to use Emergency Stop", player)
                    useEmergencyStop = pc.pollEmergencyStop(self.copyState())
                else:
                    # Player is unable
                    self.log.info("%s cannot use Emergency Stop", player)
                    useEmergencyStop = False

                # Test if a decision was made
                if useEmergencyStop is not None:
                    # Execute resolution
                    if not useEmergencyStop:
                        self.log.info("Resolving %s played by %s", card, player)
                        self._resolvePlay(player, card, target)
                    else:
                        self.log.info("%s used Emergency Stop", player)
                        player.useEmergencyStop()
                    resolved = True

            if resolved:
                # Check for winner
                self.log.debug("End of resolution. Seeing if %s won", player)
                if player.distanceToFinish() == 0:
                    self.log.info("%s has won!", player)
                    self._state.winner = self._toResolve[1][0]

                # Clear the play
                self._toResolve = None
        else:
            # Set the state to next play and tick the turn counter
            self.log.debug("End of resolution step. Ticking state to initplay")
            self._state.GMState = self._GMStates['initplay']
            self._state.turn += 1

    def _playerCanMove(self, player):
        """Determines if the player is stuck or not. If the player is stuck,
        returns None, else returns the target ship (the one the player will
        travel towards)"""
        self.log.debug("Inside %s", self._playerCanMove.__name__)
        # Set up the math
        nearestAhead = None
        nearestBehind = None
        distanceAhead = 100
        distanceBehind = 100
        numberAhead = 0
        numberBehind = 0

        # Loop over all ships on the board
        self.log.debug("Looping over all ships on the board")
        for ship in (self._state.players + self._state.hulks):
            s = ship[0]
            # Ignore the player being resolved
            if not s == player:
                # Ignore ships in the singularity
                if not s.getPos() == 0:
                    self.log.debug("Got valid ship %s on tile %i", s, s.getPos())
                    # The ship is behind the player
                    if player.directionTo(s) == -1:
                        self.log.debug("Ship is behind player")
                        numberBehind += 1
                        if player.distanceTo(s) < distanceBehind:
                            distanceBehind = player.distanceTo(s)
                            nearestBehind = s
                            self.log.debug("Ship is the closest behind at "+
                                           "distance %i", distanceBehind)
                    # The ship is ahead of the player
                    else:
                        self.log.debug("Ship is ahead of player")
                        numberAhead += 1 
                        if player.distanceTo(s) < distanceAhead:
                            distanceAhead = player.distanceTo(s)
                            nearestAhead = s
                            self.log.debug("Ship is the closest ahead at "+
                                           "distance %i", distanceAhead)

        # Determine if the player can move
        if distanceAhead == distanceBehind:
            # Equidistant. Equal numbers?
            self.log.debug("Equal distance between ships ahead and behind")
            if numberAhead == numberBehind:
                # Stuck ship
                self.log.debug("Equal number of ships on both sides. Player "+
                               "is stuck. Returning")
                return None
            else:
                # Not stuck. Determine target
                if numberAhead > numberBehind:
                    self.log.debug("More ships ahead. Target set. Returning")
                    return nearestAhead
                else:
                    self.log.debug("More ships behind. Target set. Returning")
                    return nearestBehind
        else:
            # There is a closest ship. Determine target.
            if distanceAhead < distanceBehind:
                self.log.debug("Ship ahead is closest. Target set. Returning")
                return nearestAhead
            else:
                self.log.debug("Ship behind is closest. Target set. Returning")
                return nearestBehind
    
    def _resolvePlay(self, player, card, target):
        """Resolves an individual play and moves the player accordingly"""
        self.log.debug("Inside %s", self._resolvePlay.__name__)
        if card.getType() == Card.Type.normal:
            # Normal movement
            d = player.directionTo(target)
            player.move(card.getValue() * d)
            self.log.info("Normal card %s resolved for %s, moved %i steps to "+
                          "tile %i", card, player.getName(), card.getValue(),
                          player.getPos())
            self._resolveCollision(player, d)
        elif card.getType() == Card.Type.repulsor:
            # Repulsor movement
            d = player.directionTo(target)
            player.move(card.getValue() * -d)
            self.log.info("Repulsor card %s resolved for %s, moved %i steps "+
                          "to tile %i", card, player.getName(), card.getValue(),
                          player.getPos())
            self._resolveCollision(player, -d)
        else:
            # Tractor. Bastard
            self.log.info("Tractor card %s played by %s being resolved",
                          card, player.getName())
            # Build ship list
            ships = []
            for ship in (self._state.players + self._state.hulks):
                s = ship[0]
                if not s == player:
                    ships.append(s)
            # First sort (signed, since ships closer to the singularity get
            # priority in a tie)
            self.log.debug("Sorting list of ships by distance to %s", player)
            ships = sorted(ships, key=lambda s: (player.distanceTo(s) *
                                                 player.directionTo(s)))
            # Second sort (unsigned; preserves relative order due to stable
            # sort)
            ships = sorted(ships, key=lambda s: player.distanceTo(s))
            self.log.debug("Ships will be tractored in order %s", ships)
            # Loop over sorted ships and resolve tractor
            for s in ships:
                self.log.debug("Tractoring %s", s)
                d = s.directionTo(player)
                s.move(card.getValue() * d)
                self.log.info("%s was tractored %i steps to tile %i",
                              s.getName(), card.getValue(), s.getPos())
                self._resolveCollision(s, d)

    def _resolveCollision(self, player, direction):
        """Handles post-resolution placement so that no collisions occur"""
        self.log.debug("Inside %s", self._resolveCollision.__name__)
        # Loop until all collisions handled
        while True:
            # Disregard everything if the player is in the singularity
            if not player.getPos() == 0:
                collision = False
                for ship in (self._state.players + self._state.hulks):
                    s = ship[0]
                    if not s == player:
                        if s.getPos() == player.getPos():
                            # Collision
                            collision = True
                            break
                if collision:
                    player.move(direction)
                    self.log.info("%s collided with %s. Continuing movement to"+
                                  " tile %i", player.getName(), s,
                                  player.getPos())
                else:
                    break
            else:
                break
