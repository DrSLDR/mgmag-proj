"""Module containing the code pertaining to cards"""

"""Master card class. Contains card instance data, type class and comparison
functionality"""
class Card:
    
    """Nested class acting as an enumeration over card types. For utility
    only"""
    class Type:
        normal = 0
        repulsor = 1
        tractor = 2
    
    """Constructs a card and sets instance variables. Instance variables are to
    be considered constant."""
    def __init__(self, cardtype, value, name, longname):
        self._cardtype = cardtype
        self._value = value
        self._name = name
        self._longname = longname

    """Getters. Accessing the instance variables directly is bad practice. Don't
    do it.'"""
    def getType(self):
        return self._cardtype

    def getValue(self):
        return self._value

    def getName(self):
        return self._name

    def getLongName(self):
        return self._longname

    """Test function to see if the current card resolves before a given
    card. 
    Returns true if the card should resolve first, else false."""
    def resolvesBefore(self, card):
        return self._name < card.getName()

    """ Return string describing card"""
    def __str__(self):
        return self.getName()

##### ENDs OF CARD CLASS ########################################################

"""Deck class; singleton handling the creation of a deck, shuffling and laying out the card field"""
class Deck:

    """Creates a full deck of cards, sorted, as a list"""
    def __init__(self):
        # Master deck configuration list
        DECKCONF = [
            ("Argon", "Ar", 1, Card.Type.normal),
            ("Boron", "B", 2, Card.Type.normal),
            ("Carbon", "C", 3, Card.Type.normal),
            ("Dysprosium", "Dy", 5, Card.Type.normal),
            ("Einsteinium", "Es", 2, Card.Type.normal),
            ("Flourine", "F", 6, Card.Type.normal),
            ("Gallium", "Ga", 5, Card.Type.normal),
            ("Hydrogen", "H", 4, Card.Type.normal),
            ("Iridium", "Ir", 6, Card.Type.normal),
            ("Jodium", "Jo", 2, Card.Type.tractor),
            ("Krypton", "Kr", 2, Card.Type.repulsor),
            ("Lithium", "Li", 4, Card.Type.normal),
            ("Magnesium", "Mg", 10, Card.Type.normal),
            ("Neon", "Ne", 6, Card.Type.repulsor),
            ("Oxygen", "O", 7, Card.Type.normal),
            ("Plutonium", "Pu", 5, Card.Type.normal),
            ("Sydnium", "Qt", 3, Card.Type.tractor),
            ("Radium", "Ra", 9, Card.Type.normal),
            ("Silicon", "Si", 9, Card.Type.normal),
            ("Thorium", "Th", 2, Card.Type.normal),
            ("Uranium", "U", 5, Card.Type.repulsor),
            ("Vanadium", "V", 7, Card.Type.normal),
            ("Tungsten", "W", 8, Card.Type.normal),
            ("Xenon", "Xe", 3, Card.Type.repulsor),
            ("Yttrium", "Y", 8, Card.Type.normal),
            ("Zirconium", "Zr", 7, Card.Type.normal)
        ]

        # Business end of function; puts actual cards in deck
        self.deck = [None]*len(DECKCONF)
        for i in range(len(DECKCONF)):
            conf = DECKCONF[i]
            self.deck[i] = Card(conf[3], conf[2], conf[1], conf[0])

    """Lay out cards from the deck as a recource field. 
    Returns cards in sets of 2; the second is the hidden one.
        (Does not remove the cards from self.deck, only returns the draw result. 
        This way we don't need to keep rebuilding the cards in the deck) """
    def getCardField(self,playerAmount):
        # make a resource field with size of 3*playerAmount
        import random
        # draw the right amount of (unique) cards
        cardDraws = random.sample(self.deck,2*3*playerAmount) # 2x, because of the double cards
        # put them in sets of 2
        field = [None]*(3*playerAmount)
        for i in range(0,3*playerAmount):
            # each field entry contains two cards: assume the second to be the hidden one
            field[i] = ( cardDraws[i*2] , cardDraws[i*2+1] ) 
        return field

"""print a card list"""
def printCardList(cardList):
    for i in range(len(cardList)):
        print(cardList[i])

"""print a card field"""
def printCardField(cardField):
    for i in range(len(cardField)):
        print( "[ shown: "+str(cardField[i][0])+" , hidden: "+str(cardField[i][1])+" ]")
