"""Interface for controllers, implement this to get
runtime gaurantee your controller works"""

class IPlayerController():
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""

    def __init__(self, player, args):
        self.player = player

    def _NotImplementError(self):
        """Throws an error that a subclass should implement a function
        It uses some black magic to tell which class and what function
        """
        import inspect
        raise NotImplementedError(
            "%s should implement %s!" % (
                type(self).__name__, inspect.stack()[1][3]
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

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        self._NotImplementError()
