"""Interface for controllers, implement this to get
runtime gaurantee your controller works"""

class IPlayerController():
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""

    def __init__(self, player, args):
        self.player = player
        import logging
        # give all pc's a logger
        self.log = logging.getLogger(type(self).__name__) 

    def _NotImplementError(self):
        """Throws an error that a subclass should implement a function
        It uses some black magic to tell which class and what function
        """
        import inspect
        raise NotImplementedError(
            "%s should implement %s!" % (
                # get the lowest level typename
                type(self).__name__, 
                # 0 is this stackframe, 1 is the one above
                # third argument is the functionname
                inspect.stack()[1][3] 
            )
        )

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        self._NotImplementError()

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        self._NotImplementError()

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        self._NotImplementError()

    def announceWinner(self, state):
        """Function that updates the PC after the last turn"""
        self._NotImplementError()

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        self._NotImplementError()

    def isHuman(self):
        """The board need to be able to find the human player, which this function eill help with"""
        self._NotImplementError()
