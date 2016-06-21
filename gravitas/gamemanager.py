"""Module containing the game manager class"""
from model.player import Player
from model.ship import Ship
from model.card import Card, Deck
from controller.human import Human_PC
from engine import callog
import random, logging, copy
from collections import namedtuple
from sys import maxsize

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
        self.makePT = namedtuple('PlayerTuple', 'ship pc')
        self.players = {}
        self.playerOrder = []
        self.hulks = {}
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
    def addHulk(self, name, position):
        self.hulks[name] = (self.makePT(Ship(pos=position, name=name), None))

    @callog
    def addPlayer(self, player, pc):
        self.players[player.getName()] = self.makePT(player, pc)
        self.playerOrder.append(player.getName())

    @callog
    def getPlayer(self, key):
        return self.players[key]

    @callog
    def getHulk(self, key):
        return self.hulks[key]

    @callog
    def getShip(self, key):
        if key in self.players:
            return self.getPlayer(key)
        else:
            return self.getHulk(key)

    @callog
    def getHumanPlayer(self):
        # finds the first (and assumed to be the only) human in between the players
        humans = [p for p in self.players if self.getPlayer(p).pc 
                  and self.getPlayer(p).pc.isHuman()]
        if len(humans) == 0 :
            return None
        else:
            return humans[0] # string

    @callog
    def addEventLogItem(self, player, event, info=None):
        """Adds the provided item to the event log.

        Player is the key of the player who caused the event, event is an
        integer from state.EVENTS, and info is a card if the event is DRAFT or
        PLAY, None if EMERGENCY.

        """
        item = {'player': player, 
                'event': event,
                'info': info}
        self.log.debug("Adding %s to event log", item)
        self.eventlog.append(item)

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
        be called directly from outside the State. It will return a tuple with
        the key referencing the closest (target) ship, the number of ships
        ahead, and the number of ships behind. If the player is stuck, the
        target will be None.

        """

        # Set up the math
        sur = {
            'nearAhead' : None,
            'nearBehind' : None,
            'distAhead' : 100,
            'distBehind': 100,
            'numAhead' : 0,
            'numBehind' : 0
        }
        
        def evaluateSurroundings(player, ship, sur):
            """Internal function to evaluate the player's surroundings. Directly
            modifies the parameters on the outside (yay closures)"""
            # Ignore ships in the singularity
            if not ship.getPos() == 0:
                self.log.debug("Got valid ship %s on tile %i", ship, 
                               ship.getPos())
                # The ship is behind the player
                if player.directionTo(ship) == -1:
                    self.log.debug("Ship is behind player")
                    sur['numBehind'] += 1
                    if player.distanceTo(ship) < sur['distBehind']:
                        sur['distBehind'] = player.distanceTo(ship)
                        sur['nearBehind'] = ship.getName()
                        self.log.debug("Ship is the closest behind at "+
                                       "distance %i", sur['distBehind'])
                # The ship is ahead of the player
                else:
                    self.log.debug("Ship is ahead of player")
                    sur['numAhead'] += 1
                    if player.distanceTo(ship) < sur['distAhead']:
                        sur['distAhead'] = player.distanceTo(ship)
                        sur['nearAhead'] = ship.getName()
                        self.log.debug("Ship is the closest ahead at "+
                                       "distance %i", sur['distAhead'])

        # Bind the active player tuple
        pt = self.getPlayer(player)

        # Loop over all ships on the board
        self.log.debug("Looping over all ships on the board")
        if hulks:
            for h in self.hulks:
                hulk = self.getHulk(h)
                evaluateSurroundings(pt.ship, hulk.ship, sur)

        for p in self.players:
            if not p == player:
                otherpt = self.getPlayer(p)
                evaluateSurroundings(pt.ship, otherpt.ship, sur)

        self.log.debug("Surroundings evaluated to %s", sur)

        # Determine if the player can move
        if sur['distAhead'] == sur['distBehind']:
            # Equidistant. Equal numbers?
            self.log.debug("Equal distance between ships ahead and behind")
            if sur['numAhead'] == sur['numBehind']:
                # Stuck ship
                self.log.debug("Equal number of ships on both sides. Player "+
                              "is stuck.")
                return (None, sur['numAhead'], sur['numBehind'])
            else:
                # Not stuck. Determine target
                if sur['numAhead'] > sur['numBehind']:
                    self.log.debug("More ships ahead. Target set")
                    return (sur['nearAhead'], sur['numAhead'], sur['numBehind'])
                else:
                    self.log.debug("More ships behind. Target set")
                    return (sur['nearBehind'], sur['numAhead'],
                            sur['numBehind'])
        else:
            # There is a closest ship. Determine target.
            if sur['distAhead'] < sur['distBehind']:
                self.log.debug("Ship ahead is closest. Target set")
                return (sur['nearAhead'], sur['numAhead'], sur['numBehind'])
            else:
                self.log.debug("Ship behind is closest. Target set")
                return (sur['nearBehind'], sur['numAhead'], sur['numBehind'])

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

class StateCluster:
    """State Cluster class, containing the authoritative state as well as all
    the state copies in use. Functionality handles update calls from the game
    manager so that all copies are kept in sync.

    """
    
    def __init__(self, state):
        """Initializes the state cluster"""
        self.__authoritative = state
        self.log = logging.getLogger("StateCluster")
        self._topcopy = self._copyState()
        self._playerCopies = {}

        # Build player copies
        for key in self.__authoritative.players:
            self._playerCopies[key] = self._copyState()            

    @callog
    def _copyState(self):
        """Returns a copy of the state"""
        self.log.debug("Creating semi-shallow state copy")
        state = copy.copy(self.__authoritative)

        state.playerOrder = []
        state.eventlog = []

        self.log.debug("Creating censored player list")
        state.players = {}
        for key in self.__authoritative.players:
            # This function is doing direct access to the player
            # dictionary. This is not how it is supposed to be done. Don't do
            # like this.
            pt = self.__authoritative.players[key]
            playerCopy = pt.ship.makeCensoredCopy()
            state.addPlayer(playerCopy, None)

        self.log.debug("Deepcopying hulks")
        state.hulks = copy.deepcopy(self.__authoritative.hulks)

        self.log.debug("Shallow-copying deck")
        state.deck = copy.copy(self.__authoritative.deck)

        return state

    @callog
    def getState(self, key):
        """Returns the referenced state from the cluster. If key is None, the
        topcopy is returned."""
        if key is None:
            self.log.debug("Returning topcopy")
            return self._topcopy
        else:
            self.log.debug("Returning state instance for %s", key)
            return self._playerCopies[key]

    @callog
    def getAuth(self):
        """Returns the authoritative state. This function SHOULD NEVER be called
        from outside the GameManager and should never be used for direct
        writing, even inside the GameManager.

        """
        self.log.warning("DIRECT AUTHORITATIVE STATE ACCESS")
        return self.__authoritative

    @callog
    def _setAttrib(self, attrib, value, doCopy=False):
        """Updates some root-level attribute across the cluster."""
        setattr(self.__authoritative, attrib, value)
        if doCopy:
            value = copy.copy(value)
        setattr(self._topcopy, attrib, value)
        for key in self._playerCopies:
            if doCopy:
                value = copy.copy(value)
            setattr(self._playerCopies[key], attrib, value)

    @callog
    def clusterMap(self, func, skipAuth=False):
        """Maps a function across all states in the cluster. The function must
        take a state as an argument. The function return (if any) will be
        ignored.

        """
        if not skipAuth:
            self.log.debug("Mapping onto authoritative state")
            func(self.__authoritative)
        self.log.debug("Mapping onto topcopy")
        func(self._topcopy)
        for key in self._playerCopies:
            self.log.debug("Mapping onto state for player key %s", key)
            func(self._playerCopies[key])

    @callog
    def setWinner(self, playerKey):
        """Sets the key of the winning player across the cluster."""
        self._setAttrib("winner", playerKey)

    @callog
    def setGMState(self, state):
        """Sets the Game Manager state value across the cluster."""
        self._setAttrib("GMState", state)

    @callog
    def setPlayerOrder(self, orderedList):
        """Sets the player order across the cluster."""
        self._setAttrib("playerOrder", orderedList, doCopy=True)

    @callog
    def syncDeckField(self):
        """Synchronizes the deck field across the cluster."""
        ucf = self.__authoritative.deck.updateCopyFields
        ucf(self._topcopy.deck)
        for key in self._playerCopies:
            ucf(self._playerCopies[key].deck)

    @callog
    def moveShip(self, key, move):
        """Moves a player a (signed) move distance across the cluster."""
        # Internal function that is mapped over the cluster
        def mapMove(state):
            state.getShip(key).ship.move(move)
        self.clusterMap(mapMove)

    @callog
    def tickRound(self):
        """Ticks counters over to next round."""
        r = self.__authoritative.round
        self._setAttrib("round", r + 1)
        self._setAttrib("turn", 0)

    @callog
    def tickTurn(self):
        """Ticks turn counter."""
        t = self.__authoritative.turn
        self._setAttrib("turn", t + 1)

class GameManager:
    """Game manager class. Home to all the game's logic."""

    def __init__(self, state):
        """Constructs the game manager. Takes an already-constructed
        game-state."""
        self._cluster = StateCluster(state)
        self.rng = random.Random()
        self.rng.seed(42) # requires seeding from the outside
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
        self._humanName = self._cluster.getAuth().getHumanPlayer()

    @callog
    def copyState(self, key=None):
        """Returns the clustered copy of the state"""
        return self._cluster.getState(key)

    def getHuman(self):
        if self._humanName:
            authState = self._cluster.getAuth()
            humanPlayer = authState.getPlayer(self._humanName)
            human = {}
            human['name'] = self._humanName
            human['color'] = humanPlayer.ship.getColor()
            human['hand'] = humanPlayer.ship.getHand().copy()
            human['canES'] = humanPlayer.ship.canEmergencyStop()
            return human
        else:
            return None

    @callog
    def update(self):
        """Function to update the game state. Only public function of the
        GM. Returns True if a winner has been decided."""
        authState = self._cluster.getAuth()
        if authState.winner is not None:
            self.log.info("Got winner at round %i, turn %i: %s",
                          authState.round, authState.turn,
                          authState.winner)
            self._announceWinnerToPCs()
            return True # return truth to end the game
        self.log.debug("No known winner")

        if authState.round > 5:
            self.log.info("Game is over. Figuring out winner.")
            # Figure out non-clear victory
            if authState.winner is None:
                self._sortPlayers()
                self._cluster.setWinner(self._cluster.getAuth().playerOrder[-1])

            return False # next update winner is announced

        self.log.info("Game is not over. In round %i",
                        authState.round)
        # we are to cool for function tables
        # you bet
        if authState.GMState == self.GMStates['init']:
            # Initializes the round
            self.log.info("Game is in init state")
            self._initRound()
        elif authState.GMState == self.GMStates['initdraft']:
            # Prepare the draft
            self.log.info("Game is in initdraft state")
            self._initDraft()
        elif authState.GMState == self.GMStates['drafting']:
            # Calls for drafting
            self.log.info("Game is in drafting state")
            self._draft()
        elif authState.GMState == self.GMStates['initplay']:
            # Prepare for play
            self.log.info("Game is in initplay state")
            self._initTurn()
        elif authState.GMState == self.GMStates['playing']:
            self.log.info("Game is in playing state")
            if authState.turn < 6:
                # Play game
                self.log.info("Round is not over. At turn %i",
                                authState.turn)
                self._turn()
            else:
                # End round
                self.log.info("End of round %i", authState.round)
                self._cluster.tickRound()
                self._cluster.setGMState(self.GMStates['init'])
        elif authState.GMState == self.GMStates['reveal']:
            # Reveal plays
            self.log.info("Game is in reveal state")
            self._reveal()
        elif authState.GMState == self.GMStates['resolve']:
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

        # Internal function to map over the cluster
        def doESReset(state):
            for key in state.players:
                pt = state.getPlayer(key)
                pt.ship.resetEmergencyStop()

        # Reset all players Emergency Stop
        self.log.debug("Mapping emergency stop reset function across the cluster")
        self._cluster.clusterMap(doESReset)
        # Sets the next state
        self.log.debug("Ticking game state to initdraft")
        self._cluster.setGMState(self.GMStates['initdraft'])
    
    @callog
    def _sortPlayers(self):
        """Sorts the players based on distance to the warp gate. If two or more
        players are in the singularity, their order is randomized."""
        # Pull all players in the singularity into a separate list
        self.log.debug("Sorting out players in the Singularity")
        authState = self._cluster.getAuth()
        inS = []
        playerOrder = copy.copy(authState.playerOrder)
        for p in authState.players:
            pt = authState.getPlayer(p)
            if pt.ship.getPos() == 0:
                self.log.debug("Player %s is in the Singularity. Will be"+
                               " shuffled", pt.ship)
                inS.append(p)

        # Pull players in the singularity from the main player list
        for p in inS:
            self.log.debug("Removing %s from the player list", p)
            playerOrder.remove(p)
        # Shuffle the players in the singularity
        self.rng.shuffle(inS)
        # Sort the remaining players
        playerOrder = sorted( playerOrder, key=lambda p:
            authState.getPlayer(p).ship.distanceToFinish())
        # Concatenate
        playerOrder += inS
        # Reverse
        playerOrder.reverse()
        self._cluster.setPlayerOrder(playerOrder)
        self.log.debug("Order of players is now %s", playerOrder)

    @callog
    def _initDraft(self):
        """Initializes the drafting step. Prepares the field and sets the
        drafting parameters."""
        authState = self._cluster.getAuth()
        self._field = authState.deck.createCardField(len(authState.players))
        self._cluster.syncDeckField()
        self.log.info("Generated fields %s", self._field)
        self._draftsRemaining = 3
        self._draftPlayer = 0
        # Sets drafting
        self.log.debug("Ticking state to drafting")
        self._cluster.setGMState(self.GMStates['drafting'])

    @callog
    def _draft(self):
        """Updates the drafting step. Polls the next player in line for a
        choice. Updates the state to playing when all drafting is done."""
        authState = self._cluster.getAuth()
        key = authState.playerOrder[self._draftPlayer]
        pt = authState.getPlayer(key)
        self.log.debug("Current field is %s",
                       authState.deck.percieveCardField())
        self.log.info("Polling %s to draft", pt.ship)
        selection = pt.pc.pollDraft(self.copyState(key=key))

        # Internal function to handle draft across the cluster
        # Closures, fuck yeah
        def handleDraft(state):
            cards = state.deck.takeFromField(selection)
            state.addEventLogItem(player=key,
                                  event=state.EVENT['DRAFT'], 
                                  info=cards[0])
        
        # Handle draft
        if selection is not None:
            self.log.debug("Got field index %i. Handling draft", selection)
            cards = authState.deck.takeFromField(selection)
            self.log.info("%s drafted cards %s", pt.ship, cards)
            pt.ship.addCards(cards)
            self.log.debug("Visible card was %s", cards[0])
            self.log.debug("Hand of %s is now %s", pt.ship,
                           pt.ship.getHand()) 
            self._cluster.clusterMap(handleDraft, skipAuth=True)
            self._draftPlayer += 1
            if self._draftPlayer == len(authState.players):
                self._draftsRemaining -= 1
                self._draftPlayer = 0

        # Check if draft is ended
        if self._draftsRemaining == 0:
            # End drafting
            self.log.debug("End of drafting. Ticking state to initplay")
            self._cluster.setGMState(self.GMStates['initplay'])

    @callog
    def _turn(self):
        """Turn update function. Polls a player to play."""
        # Gets the player to poll
        key = self._turnSelectPlayer()
        pt = self._cluster.getAuth().getPlayer(key)
        # Get play
        self.log.info("Polling %s to play", pt.ship)
        play = pt.pc.pollPlay(self.copyState(key=key))

        # Handle play
        if play is not None:
            self.log.info("%s played %s", pt.ship, play)
            self._plays[play] = key
            pt.ship.playCard(play)
            self.log.debug("Plays are now %s", self._plays)
            self.log.debug("Hand of %s is now %s", pt.ship,
                           pt.ship.getHand())
            self._playersRemaining.remove(key)
        # Update state if neccessary
        if len(self._playersRemaining) == 0:
            self._cluster.setGMState(self.GMStates['reveal'])

    @callog
    def _initTurn(self):
        """Turn initialization function. Prepares the plays dictionary, players
        remaining list."""
        # Prepares dictionary containing mappings of cards to players
        self._plays = {}
        # Prepares list of players which have yet to play
        self._playersRemaining = copy.copy(self._cluster.getAuth().playerOrder)
        # Sets the state to playing
        self.log.debug("Ticking state to playing")
        self._cluster.setGMState(self.GMStates['playing'])

    @callog
    def _turnSelectPlayer(self):
        """Selects a random player to poll for play. Uses randomization since
        playing does not have to be in order."""
        self.log.debug("Remaining players are %s", self._playersRemaining)
        return self.rng.choice(self._playersRemaining)

    @callog
    def _reveal(self):
        """Turn reveal. Sends revealed cards to all player controllers. Also
        prepares resolution."""
        # Informs all PCs
        authState = self._cluster.getAuth()
        for key in authState.players:
            pt = authState.getPlayer(key)
            self.log.debug("Informing %s of plays", pt.ship)
            pt.pc.informReveal(copy.copy(self._plays))

        # Internal function to map out the event log
        def recordPlays(state):
            for play in self._plays:
                state.addEventLogItem(player=self._plays[play],
                                      event=state.EVENT['PLAY'],
                                      info=play)

        # Write plays to event log
        self.log.debug("Writing plays to event log")
        self._cluster.clusterMap(recordPlays)

        # Prepares the resolution
        self._orderedPlays = Deck.sortByResolution(self._plays)
        self.log.info("Order of resolution will be %s", self._orderedPlays)
        self._toResolve = None

        # Updates state
        self.log.debug("Ticking state to resolve")
        self._cluster.setGMState(self.GMStates['resolve'])

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
        authState = self._cluster.getAuth()

        # turn _plays into a dict of cardNames and player-colours
        cardOwnerColorNr = {}
        for cardKey in self._plays:
            cardOwnerColorNr[cardKey.getName()] = authState.players[self._plays[cardKey]].ship.getColor()

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
            self._cluster.setGMState(self.GMStates['initplay'])
            self._cluster.tickTurn()
            return

        # Bind the relevant variables
        authState = self._cluster.getAuth()
        card = self._toResolve[0]
        key = self._toResolve[1]
        pt = authState.getPlayer(key)
        resolved = False
        self.log.debug("Attempting to resolve play %s by %s", card, pt.ship)

        # Determine if the player can move
        target = authState.getTarget(key)
        if target is not None or card.getType() == Card.Type.tractor:
            # Player can move. Test if Emergency Stop is available
            self.log.debug("Player isn't stuck. Targeting %s. Resolution "+
                           "continues", target)
            if pt.ship.canEmergencyStop():
                # Player is able; poll
                self.log.info("Polling %s to use Emergency Stop", pt.ship)
                useEmergencyStop = pt.pc.pollEmergencyStop(
                    self.copyState(key=key))
            else:
                # Player is unable
                self.log.info("%s cannot use Emergency Stop", pt.ship)
                useEmergencyStop = False

            # Internal function to map in the event Emergency Stop was used
            def uES(state):
                mappt = state.getPlayer(key)
                mappt.ship.useEmergencyStop()
                state.addEventLogItem(player=key,
                                      event=state.EVENT['EMERGENCY'])

            # Test if a decision was made
            if useEmergencyStop is not None:
                # Execute resolution
                if not useEmergencyStop:
                    self.log.info("Resolving %s played by %s", card, pt.ship)
                    self._resolvePlay(key, card, target)
                else:
                    self.log.info("%s used Emergency Stop", pt.ship)
                    self._cluster.clusterMap(uES)
                resolved = True

        else:
            self.log.info("%s is stuck and cannot move", pt.ship)
            resolved = True

        if resolved:
            # Check for winner
            self.log.debug("End of resolution. Seeing if %s won", pt.ship)
            if pt.ship.distanceToFinish() == 0:
                self.log.info("%s has won!", pt.ship)
                self._cluster.setWinner(key)

            # Clear the play
            self._toResolve = None

    @callog
    def _resolvePlay(self, key, card, target):
        """Resolves an individual play and moves the player accordingly"""
        authState = self._cluster.getAuth()
        pt = authState.getPlayer(key)
        if card.getType() == Card.Type.normal:
            # Normal movement
            tpt = authState.getShip(target)
            d = pt.ship.directionTo(tpt.ship)
            self._cluster.moveShip(key, card.getValue() * d)
            self.log.info("Normal card %s resolved for %s, moved %i steps to "+
                          "tile %i", card, key, card.getValue(),
                          pt.ship.getPos())
            self._resolveCollision(key, d)
        elif card.getType() == Card.Type.repulsor:
            # Repulsor movement
            tpt = authState.getShip(target)
            d = pt.ship.directionTo(tpt.ship)
            self._cluster.moveShip(key, card.getValue() * -d)
            self.log.info("Repulsor card %s resolved for %s, moved %i steps "+
                          "to tile %i", card, key, card.getValue(),
                          pt.ship.getPos())
            self._resolveCollision(key, -d)
        else:
            # Tractor. Bastard
            self.log.info("Tractor card %s played by %s being resolved", card,
                          key)
            # Build ship list
            ships = (list(authState.players.keys()) +
                     list(authState.hulks.keys()))
            ships.remove(key)
            
            # First sort (signed, since ships closer to the singularity get
            # priority in a tie)
            self.log.debug("Sorting list of ships by distance to %s", key)
            ships = sorted( ships, key=lambda s:
                (pt.ship.distanceTo(authState.getShip(s).ship) *
                pt.ship.directionTo(authState.getShip(s).ship)))
            # Second sort (unsigned; preserves relative order due to stable
            # sort)
            ships = sorted(ships, key=lambda s:
                           pt.ship.distanceTo(authState.getShip(s).ship))
            self.log.debug("Ships will be tractored in order %s", ships)
            # Loop over sorted ships and resolve tractor
            for s in ships:
                tpt = authState.getShip(s)
                self.log.debug("Tractoring %s", s)
                d = tpt.ship.directionTo(tpt.ship)
                self._cluster.moveShip(s, card.getValue() * d)
                self.log.info("%s was tractored %i steps to tile %i",
                              s, card.getValue(), tpt.ship.getPos())
                self._resolveCollision(s, d)

    @callog
    def _resolveCollision(self, key, direction):
        """Handles post-resolution placement so that no collisions occur"""
        # Disregard everything if the player is in the singularity
        collision = False
        authState = self._cluster.getAuth()
        pt = authState.getShip(key)
        if not pt.ship.getPos() == 0:
            ships = (list(authState.players.keys()) +
                     list(authState.hulks.keys()))
            ships.remove(key)
            for t in ships:
                tpt = authState.getShip(t)
                if tpt.ship.getPos() == pt.ship.getPos():
                    # Collision
                    collision = True
                    break
            if collision:
                self._cluster.moveShip(key, direction)
                self.log.info("%s collided with %s. Continuing movement to "+
                              "tile %i", key, t, pt.ship.getPos())
                self._resolveCollision(key, direction)

    @callog
    def _announceWinnerToPCs(self):
        """Hands over the state to each player after the game has ended"""
        authState = self._cluster.getAuth()
        for p in authState.players:
            authState.getPlayer(p).pc.announceWinner(self.copyState(key=p))
