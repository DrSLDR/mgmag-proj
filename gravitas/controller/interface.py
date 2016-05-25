"""Interface for controllers, implement this to get
runtime gaurantee your controller works"""

class IPlayerController():
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""

    def __init__(self, player, args):
        self.player = player

    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        raise NotImplementedError("Subclasses should implement this!")

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        raise NotImplementedError("Subclasses should implement this!")

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        raise NotImplementedError("Subclasses should implement this!")

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        raise NotImplementedError("Subclasses should implement this!")
