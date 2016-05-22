"""Every file should start with a comment describing its purpose in life"""

def function(argument, bars):
    """ Docstrings below the decleration according to the 
    [pep](https://www.python.org/dev/peps/pep-0257/#id15)

    Note that you don't have to jam everything in classes, this
    function is a member of example.function by default.

    Also note that I'm avoiding the 80 collumn markers, although its not a hard
    limit
    """
    print("this %s" % argument)

    for bar in bars:
        """Collections should be plural, so you can iterate trough them
        like above, which is an 'almost' sentence, something which I strive
        for"""

        print("look a nice %s, so nice" % bar)
        """Please, use formating instead of concatination, for more
        information see: https://docs.python.org/3/library/string.html
        they use .format everywhere but % is a shorthand.
        """

def createFace(size, isSmiling):
    """functions are in pascal Case, so are function arguments"""
    def nestedFace(doesExist):
        """Nested functions are prefereable, although they should be
        short-ish"""

class House():
    """Classes start in camel case"""
    def __init__(self, hasWindows):
        """For boolean values please use is/has/can etc"""

        self.coolfactor = 4 if hasWindows else 1000
        """Please use conditional assignments like this, its beautifull"""


class RoadHouse(House):
    """For extention its conventional to mention the direct parent in the 
    name, but you can have reasons to avoid it (usually not though)."""


bars = [3,4,5]

while True:
    if len(bars) < 3:
        break
    """Avoid else statements like the plague, use early return like
    structures instead (usually involving a return or a break such
    as in this case, it usually also involves flipping the logic)"""

even = filter(lambda x: x % 2 == 0, bars)
"""Do learn and use the combinators, they can save you so much time
and if you know them they make your code so much more readable,
seriously [every](https://stackoverflow.com/questions/26196/filtering-collections-in-c-sharp),
[language](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter)
[has](http://www.cplusplus.com/reference/algorithm/remove_if/) 
[them](https://www.safaribooksonline.com/library/view/scala-cookbook/9781449340292/ch10s18.html) """

class NamingVerbosity():
    """On naming verbosity, classes should be the most precisely named,
    you can seriously take a couple of minutes to think of a good named
    for a class, because it'll be shown everywhere"""

    def bakePizza(self, pizzas):
        """Method names should also be quite accurate, and usually be
        in imperative  mood, argument names can be shorter, but please
        avoid abbreviations"""
