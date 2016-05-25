"""Interface for controllers, implement this to get
runtime gaurantee your controller works"""

class IPlayerController():
    """Interface for implementing the PC's. Used to make the underlying type of PC transparent the game manager"""

    def __init__(self, player, args):
        self.player = player

    #TODO replace return none with: 
    # raise NotImplementedError("Subclasses should implement this!")
    def pollDraft(self, state):
        """Function that returns the choice of a stack from the draw field"""
        return None # returns None because it is an abstract function

    def pollPlay(self, state):
        """Function that returns which card the PC want to play"""
        return None # returns None because it is an abstract function

    def pollEmergencyStop(self, state):
        """Function that returns the choice of using the emergency stop as a boolean"""
        return None # returns None because it is an abstract function

    def informReveal(self, cards):
        """Informs the PlayerController of the cards which have been played"""
        return None # returns None because it is an abstract function
