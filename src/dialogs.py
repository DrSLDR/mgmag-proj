from pgu import gui
from strings import Logo
class HelpDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Help")

        doc = gui.Document(width=800)

        space = title.style.font.size(" ")

        doc.block(align=-1)
        doc.add(gui.Image(Logo.game),align=1)
        for word in """Cuzco's Paint is a revolutionary new paint program it has all the awesome features that you need to paint really great pictures.""".split(" "):
            doc.add(gui.Label(word))
            doc.space(space)
        doc.br(space[1])

        doc.block(align=-1)
        for word in """This help isn't really here for any other reason than to have a help dialog.""".split(" "):
            doc.add(gui.Label(word))
            doc.space(space)

        gui.Dialog.__init__(self,title,doc)

class QuitDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Quit")

        t = gui.Table()

        t.tr()
        t.add(gui.Label("Are you sure you want to quit?"),colspan=2)

        t.tr()
        e = gui.Button("Okay")
        e.connect(gui.CLICK,self.send,gui.QUIT)
        t.td(e)

        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.close,None)
        t.td(e)

        gui.Dialog.__init__(self,title,t)

class WelcomeDialog(gui.Dialog):
    def __init__(self,**params):
        title = gui.Label("Welcome")

        doc = gui.Document(width=800)

        space = title.style.font.size(" ")

        doc.block(align=-1)
        doc.add(gui.Image(Logo.game),align=1)
        for word in """Welcome to gravitas, the game where you, have dug yourself into a hole and try to get out, however, you have to use clever words in certain combinations to try and push your oponents back into the hole. Can you regain face?!""".split(" "):
            doc.add(gui.Label(word))
            doc.space(space)

        gui.Dialog.__init__(self,title,doc)
