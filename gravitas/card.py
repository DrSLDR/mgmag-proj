"""Module containing the code pertaining to cards"""
import random

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

    """ Return string describing card"""
    def __str__(self):
        return self.getName()

    """Return unambiguos card represenation. Whatever that is."""
    def __repr__(self):
        return self.__str__()

##### ENDs OF CARD CLASS ########################################################

"""Deck class; singleton handling the creation of a deck, shuffling and laying
out the card field"""
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
        self._deck = [None]*len(DECKCONF)
        for i in range(len(DECKCONF)):
            conf = DECKCONF[i]
            self._deck[i] = Card(conf[3], conf[2], conf[1], conf[0])

        # field is empty for now
        self._field = []

    """make a resource field with size of 3*playerAmount
    Returns cards in sets of 2; the second is the hidden one.

    (Does not remove the cards from self.deck, only returns the resulting field.
    This way we don't need to keep rebuilding the cards in the deck)
    """
    def createCardField(self,playerAmount):
        # draw the right amount of (unique) cards
        # 2x, because of the double cards
        cardDraws = random.sample(self._deck,2*3*playerAmount)

        # put them in sets of 2
        self._field = [None]*(3*playerAmount)
        for i in range(0,3*playerAmount):
            # each field entry contains two cards: assume the second to be the
            # hidden one
            self._field[i] = ( cardDraws[i*2] , cardDraws[i*2+1] ) 
        return self._field

    """Players should only see the top cards in the resource field"""
    def percieveCardField(self):
        perception = []
        i = 0
        for f in self._field:
            # return for each card set (that has not been taken yet) the index
            # and the shown card
            if f is not None:
                perception.append( ( i, f[0]) )
            i += 1
        return perception

    """Gets the field"""
    def getField(self):
        return self._field

    """Removes selected cardSet of the resource field"""
    def takeFromField(self, cardIndex):
        cardSet = self._field[cardIndex]
        # make item on field None to show it has been taken. None instead of
        # removing item, because the field needs to be drawn on screen
        self._field[cardIndex] = None
        return cardSet

    """print a card list"""
    def printCardList(cardList):
        for c in cardList:
            print(c)

    """print a card field"""
    def printCardField(cardField):
        for c in cardField:
            if c is not None:
                print( "[ shown: "+str(c[0])+" , hidden: " +str(c[1])+" ]")
            else:
                print("[ Empty spot ]")

    """Sorts a given list by resolution order (alphabetic). Returns sorted list."""
    def sortByResolution(cardList):
        return sorted(cardList, key=lambda c: c.getName())
