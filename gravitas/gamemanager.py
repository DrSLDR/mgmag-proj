"""Module containing the game manager class"""
from model.player import Player
from model.ship import Ship
from model.card import Card, Deck
from controller.human import Human_PC
from engine import callog
import random, logging, copy

class State:
    """The game state class. Beyond counters relating to the point in play, it
    also contains the reference to the deck and the lists of players (and
    hulks). The player list is a dictionary from unique player names to player
    tuples (Player (or Ship) object, PlayerController (or None for hulks)).

    The State should be treated as read-only; only the Game Manger (and Factory)
    should write the state. For security, all entities reading the State should
    call the GameManager's copyState function to get a censored, unique copy.

    """
    def __init__(self):
       # Bookkeeping
        self.turn = 0
        self.round = 0
        self.players = []
        self.hulks = []
        self.winner = None
        self.deck = Deck()
        self.GMState = 0
        self.eventlog = []
        self.EVENT = {
            "DRAFT"     : 0,
            "PLAY"      : 1,
            "EMERGENCY" : 2
        }
        self.log = logging.getLogger("state")

    @callog
    def addHulk(self, position):
        self.hulks.append((Ship(pos=position), None))

    @callog
    def addPlayer(self, player):
        self.players.append(player)

    @callog
    def getHumanPlayer(self):
        # finds the first (and assumed to be the only) human in between the players
        humans = [p for p in self.players if p[1] and p[1].isHuman()]
        if len(humans) == 0 :
            return None
        else:
            return humans[0][0]

    @callog
    def addEventLogItem(self, item):
        """Adds the provided item to the event log. Item must be a dictionary
        type object with the format { "player" : Reference to the player who
        commited the action; "event" : Type of event. This can be DRAFT, PLAY,
        EMERGENCY; "info" : Details. Card, if DRAFT or PLAY, None if EMERGENCY }

        """
        self.log.debug("Adding %s to event log", item)
        self.eventlog.append(item)
        #TODO rewrite

    @callog
    def getLastEvents(self, number=1):
        """Returns the last item from the event log. If number is specified, a
        list of that many items are returned instead.

        """
        if number == 1:
            es = self.eventlog[-1]
        else:
            es = self.eventlog[-number:]
        return es

    @callog
    def _playerSurroundings(self, player, hulks=True):
        """Determines the player surroundings. This function is not intended to
        be called directly from outside the State. It will return a tuple with a
        reference to the closest (target) ship, the number of players ahead, and
        the number of players behind. If the player is stuck, the target will be
        None.

        """
        # Set up the math
        nearestAhead = None
        nearestBehind = None
        distanceAhead = 100
        distanceBehind = 100
        numberAhead = 0
        numberBehind = 0

        # Loop over all ships on the board
        self.log.debug("Looping over all ships on the board")
        if hulks:
            shiplist = self.players + self.hulks
        else:
            shiplist = self.players
        for ship in shiplist:
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
                              "is stuck.")
                return (None, numberAhead, numberBehind)
            else:
                # Not stuck. Determine target
                if numberAhead > numberBehind:
                    self.log.debug("More ships ahead. Target set")
                    return (nearestAhead, numberAhead, numberBehind)
                else:
                    self.log.debug("More ships behind. Target set")
                    return (nearestBehind, numberAhead, numberBehind)
        else:
            # There is a closest ship. Determine target.
            if distanceAhead < distanceBehind:
                self.log.debug("Ship ahead is closest. Target set")
                return (nearestAhead, numberAhead, numberBehind)
            else:
                self.log.debug("Ship behind is closest. Target set")
                return (nearestBehind, numberAhead, numberBehind)

    @callog
    def getTarget(self, player):
        """Returns the target ship of the player, i.e. the closest ship. Returns
        None if the player is stuck.

        """
        return self._playerSurroundings(player)[0]

    @callog
    def getShipsAhead(self, player, hulks=True):
        """Returns the number of ships ahead of the player. If hulks is set to
        False, hulks will be discounted so that only player ships are counted.

        """
        return self._playerSurroundings(player, hulks=hulks)[1]

    @callog
    def getShipsBehind(self, player, hulks=True):
        """Returns the number of ships behind the player. If hulks is set to
        False, hulks will be discounted so that only player ships are counted.

        """
        return self._playerSurroundings(player, hulks=hulks)[2]

class GameManager:
    """Game manager class. Home to all the game's logic."""

    def __init__(self, state):
        """Constructs the game manager. Takes an already-constructed
        game-state."""
        self._state = state
        self.log = logging.getLogger(__name__)
        self.GMStates = {
            "init" : 0,
            "initdraft" : 1,
            "drafting" : 2,
            "initplay" : 3,
            "playing" : 4,
            "reveal" : 5,
            "resolve" : 6
        }
        self._toResolve = None
        self._orderedPlays = []
        self._plays = []
        self._human = self._state.getHumanPlayer()

    @callog
    def copyState(self):
        """Returns a copy of the state"""
        self.log.debug("Creating semi-shallow state copy")
        state = copy.copy(self._state)
        
        self.log.debug("Creating censored player list")
        state.players = []
        mappings = {}
        for (player, pc) in self._state.players:
            self.log.debug("Censoring %s", player)
            playerCopy = player.makeCensoredCopy()
            state.addPlayer((playerCopy, None))
            mappings[player] = playerCopy

        # self.log.debug("Writing new state event log")
        # state.eventlog = []
        # for event in self._state.eventlog:
        #     self.log.debug("Rewriting %s", event)
        #     state.addEventLogItem({'player': mappings[event['player']],
        #                            'event': event['event'],
        #                            'info': event['info']})

        self.log.debug("Deepcopying hulks")
        hulks = copy.deepcopy(self._state.hulks)
        state.hulks = hulks

        self.log.debug("Deepcopying deck")
        state.deck = copy.deepcopy(self._state.deck)

        return state

    def getHuman(self):
        return self._human

    @callog
    def update(self):
        """Function to update the game state. Only public function of the
        GM. Returns True if a winner has been decided."""
        if self._state.winner is not None:
            self.log.info("Got winner at round %i, turn %i: %s",
                          self._state.round, self._state.turn,
                          self._state.winner.getName())
            return True # return truth to end the game
        self.log.debug("No known winner")

        if self._state.round > 5:
            self.log.info("Game is over. Figuring out winner.")
            # Figure out non-clear victory
            if self._state.winner is None:
                self._sortPlayers()
                self._state.winner = self._state.players[0][0]
            return False # next update winner is announced

        self.log.info("Game is not over. In round %i",
                        self._state.round)
        # we are to cool for function tables
        # you bet
        if self._state.GMState == self.GMStates['init']:
            # Initializes the round
            self.log.info("Game is in init state")
            self._initRound()
        elif self._state.GMState == self.GMStates['initdraft']:
            # Prepare the draft
            self.log.info("Game is in initdraft state")
            self._initDraft()
        elif self._state.GMState == self.GMStates['drafting']:
            # Calls for drafting
            self.log.info("Game is in drafting state")
            self._draft()
        elif self._state.GMState == self.GMStates['initplay']:
            # Prepare for play
            self.log.info("Game is in initplay state")
            self._initTurn()
        elif self._state.GMState == self.GMStates['playing']:
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
                self._state.GMState = self.GMStates['init']
        elif self._state.GMState == self.GMStates['reveal']:
            # Reveal plays
            self.log.info("Game is in reveal state")
            self._reveal()
        elif self._state.GMState == self.GMStates['resolve']:
            # Resolve plays; may set winner
            self.log.info("Game is in resolve state")
            self._resolve()
        return False

    @callog
    def _initRound(self):
        """Initializes the round. Sorts the players, resets all Emergency Stops,
        readies a drafting field, and sets the state to drafting."""
        # Sort the players
        self._sortPlayers()
        # Reset all players Emergency Stop
        for p in self._state.players:
            self.log.debug("Resetting Emergency Stop of player %s", p[0])
            p[0].resetEmergencyStop()
        # Sets the next state
        self.log.debug("Ticking game state to initdraft")
        self._state.GMState = self.GMStates['initdraft']
    
    @callog
    def _sortPlayers(self):
        """Sorts the players based on distance to the warp gate. If two or more
        players are in the singularity, their order is randomized."""
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

    @callog
    def _initDraft(self):
        """Initializes the drafting step. Prepares the field and sets the
        drafting parameters."""
        self._field = self._state.deck.createCardField(len(self._state.players))
        self.log.info("Generated fields %s", self._field)
        self._draftsRemaining = 3
        self._draftPlayer = 0
        # Sets drafting
        self.log.debug("Ticking state to drafting")
        self._state.GMState = self.GMStates['drafting']

    @callog
    def _draft(self):
        """Updates the drafting step. Polls the next player in line for a
        choice. Updates the state to playing when all drafting is done."""
        player = self._state.players[self._draftPlayer]
        self.log.debug("Current field is %s",
                       self._state.deck.percieveCardField())
        self.log.info("Polling %s to draft", player[0])
        selection = player[1].pollDraft(self.copyState())
        
        # Handle draft
        if selection is not None:
            self.log.debug("Got field index %i. Handling draft", selection)
            cards = self._state.deck.takeFromField(selection)
            self.log.info("%s drafted cards %s", player[0], cards)
            player[0].addCards(cards)
            self.log.debug("Visible card was %s", cards[0])
            self._state.addEventLogItem({'player': player[0],
                                         'event': self._state.EVENT['DRAFT'],
                                         'info': cards[0]})
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
            self._state.GMState = self.GMStates['initplay']

    @callog
    def _turn(self):
        """Turn update function. Polls a player to play."""
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
            self._state.GMState = self.GMStates['reveal']

    @callog
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
        self.log.debug("Ticking state to playing")
        self._state.GMState = self.GMStates['playing']

    @callog
    def _turnSelectPlayer(self):
        """Selects a random player to poll for play. Uses randomization since
        playing does not have to be in order."""
        self.log.debug("Remaining players are %s", self._playersRemaining)
        return random.choice(self._playersRemaining)

    @callog
    def _reveal(self):
        """Turn reveal. Sends revealed cards to all player controllers. Also
        prepares resolution."""
        # Informs all PCs
        cards = list(self._plays.keys())
        for p in self._state.players:
            self.log.debug("Informing %s of plays", p[0])
            p[1].informReveal(cards)

        # Write plays to event log
        self.log.debug("Writing plays to event log")
        for play in self._plays:
            self.log.debug("Handling play %s by %s", play, self._plays[play])
            self._state.addEventLogItem({'player':self._plays[play][0],
                                         'event':self._state.EVENT['PLAY'],
                                         'info':play})

        # Prepares the resolution
        self._orderedPlays = Deck.sortByResolution(self._plays)
        self.log.info("Order of resolution will be %s", self._orderedPlays)
        self._toResolve = None

        # Updates state
        self.log.debug("Ticking state to resolve")
        self._state.GMState = self.GMStates['resolve']

    @callog
    def _initNextResolve(self):
        """Prepares the next play to be resolved."""
        if len(self._orderedPlays) > 0:
            firstCard = self._orderedPlays.pop(0)
            self._toResolve = (firstCard, self._plays[firstCard])
            self.log.debug("Next card to resolve is %s", firstCard)

    @callog
    def getPlayedCards(self):
        """Function that gets the ordered card-keys, and the playsDictionary, 
        so that the board can display them"""

        # turn _plays into a dict of cardNames and player-colours
        cardOwnerColorNr = {}
        for cardKey in self._plays:
            print(cardKey)
            cardOwnerColorNr[cardKey.getName()] = self._plays[cardKey][0].getColor()

        if self._toResolve is None:
            return (self._orderedPlays.copy(),cardOwnerColorNr)
        else:
            return ([self._toResolve[0]]+self._orderedPlays.copy(), cardOwnerColorNr)

    @callog
    def _resolve(self):
        """Turn resolution. Attempts to resolve the first card in the ordered
        play list. Will poll (applicable) players to use the Emergency Stop. Can
        also set the game winner if applicable."""
        # Check if there is a play to resolve
        if self._toResolve is None:
            self.log.debug("No next resolution is set")
            # Bind the first card to be resolved
            self._initNextResolve()
        
        # Check again; if this passes, resolution is all done
        if self._toResolve is None:
            # Set the state to next play and tick the turn counter
            self.log.debug("End of resolution step. Ticking state to initplay")
            self._state.GMState = self.GMStates['initplay']
            self._state.turn += 1
            return

        # Bind the relevant variables
        card = self._toResolve[0]
        player = self._toResolve[1][0]
        pc = self._toResolve[1][1]
        resolved = False
        self.log.debug("Attempting to resolve play %s by %s", card, player)

        # Determine if the player can move
        target = self._state.getTarget(player)
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
                    self._state.addEventLogItem(
                        {'player':player,
                         'event':self._state.EVENT['EMERGENCY'],
                         'info':None})
                resolved = True

        else:
            self.log.info("%s is stuck and cannot move", player)
            resolved = True

        if resolved:
            # Check for winner
            self.log.debug("End of resolution. Seeing if %s won", player)
            if player.distanceToFinish() == 0:
                self.log.info("%s has won!", player)
                self._state.winner = self._toResolve[1][0]

            # Clear the play
            self._toResolve = None

    @callog
    def _resolvePlay(self, player, card, target):
        """Resolves an individual play and moves the player accordingly"""
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

    @callog
    def _resolveCollision(self, player, direction):
        """Handles post-resolution placement so that no collisions occur"""
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
