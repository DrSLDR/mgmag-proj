import sys, pygame
from pgu import gui
#pygame.init()

#size = width, height = 920, 840
#speed = [1, 2]
#black = 0, 0, 255

#screen = pygame.display.set_mode(size)

#ball = pygame.image.load("../img/gravitas_logo.png")
#ballrect = ball.get_rect()

#while 1:
    #for event in pygame.event.get():
        #if event.type == pygame.QUIT: sys.exit()

    #ballrect = ballrect.move(speed)
    #if ballrect.left < 0 or ballrect.right > width:
        #speed[0] = -speed[0]
    #if ballrect.top < 0 or ballrect.bottom > height:
        #speed[1] = -speed[1]

    #screen.fill(black)
    #screen.blit(ball, ballrect)
    #pygame.display.flip()

class Painter(gui.Widget):
    def __init__(self,**params):
        gui.Widget.__init__(self,**params)

        self.surface = None
        self.state = 0

        from strings import Logo

        self.cuzco = pygame.image.load(Logo.game)
        self.ballrect = self.cuzco.get_rect()

    def init(self,v):
        self.surface = pygame.Surface((int(v['width']),int(v['height'])))
        color = v['color']
        if v['color'] == 'custom':
            color = v['custom']
        else: color = pygame.Color(color)
        self.surface.fill(color)
        self.overlay = pygame.Surface((int(v['width']),int(v['height'])),pygame.SRCALPHA,32)
        self.repaint()

    def event(self,e):
        if not self.surface: return

        if e.type == gui.MOUSEBUTTONDOWN:
            print("MOOOOOOUUUUSEEEEEE")
        if e.type == gui.MOUSEMOTION:
            print("DANCE!!!!")
        if e.type is gui.MOUSEBUTTONUP:
            print("JUMPPP")

    ##The Painter class has its own paint method to render the painting surface and overlay.
    ##::
    def paint(self,s):
        size = width, height = 920, 840
        speed = [1, 2]
        self.ballrect = self.ballrect.move(speed)
        if self.ballrect.left < 0 or self.ballrect.right > width:
            speed[0] = -speed[0]
        if self.ballrect.top < 0 or self.ballrect.bottom > height:
            speed[1] = -speed[1]

        black = 0, 0, 255 # which is blue
        s.fill(black)
        # YOU JUST GOT RECT!
        s.blit(self.cuzco, self.ballrect)
        pygame.display.flip()

    ##

class App(gui.Desktop):
    def __init__(self,**params):
        from dialogs import HelpDialog, QuitDialog, WelcomeDialog
        gui.Desktop.__init__(self,**params)

        self.connect(gui.QUIT,self.quit,None)

        c = gui.Container(width=940,height=980)
        spacer = 8

        self.fname = 'untitled.tga'

        self.quit_d = QuitDialog()
        self.quit_d.connect(gui.QUIT,self.quit,None)

        self.help_d = HelpDialog()

        ##Initializing the Menus, we connect to a number of Dialog.open methods for each of the dialogs.
        ##::
        menus = gui.Menus([
            ('File/Exit',self.quit_d.open,None),
            ('Help/Help',self.help_d.open,None)
            ])
        ##
        c.add(menus,0,0)
        menus.rect.w,menus.rect.h = menus.resize()
        #print 'menus',menus.rect

        ##We utilize a Toolbox.  The value of this widget determins how drawing is done in the Painter class.
        ##::
        self.mode = mode = gui.Toolbox([
            ('Draw','draw'),
            ('Box','box'),
            ('Circle','circle'),
            ('Cuzco','cuzco'),
            ],cols=1,value='draw')
        ##
        c.add(mode,0,menus.rect.bottom+spacer)
        mode.rect.x,mode.rect.y = mode.style.x,mode.style.y
        mode.rect.w,mode.rect.h = mode.resize()
        #mode._resize()

        self.color = "#000000"

        self.painter = Painter(width=c.rect.w-mode.rect.w-spacer*2,height=c.rect.h-menus.rect.h-spacer*2,style={'border':1})
        c.add(self.painter,mode.rect.w+spacer,menus.rect.h+spacer)
        self.painter.init({'width':956,'height':956,'color':'#ffffff'})
        self.painter.rect.w,self.painter.rect.h = self.painter.resize()
        #self.painter._resize()

        welcome_d = WelcomeDialog()
        self.connect(gui.INIT,welcome_d.open,None)

        self.widget = c

    def action_new(self,value):
        self.new_d.close()
        self.fname = 'untitled.tga'
        self.painter.init(self.new_d.value.results())

    def action_save(self,value):
        pygame.image.save(self.painter.surface,self.fname)

    def action_saveas(self,value):
        self.save_d.close()
        self.fname = self.save_d.value['fname'].value
        pygame.image.save(self.painter.surface,self.fname)

    def action_open(self,value):
        self.open_d.close()
        self.fname = self.open_d.value['fname']
        self.painter.surface = pygame.image.load(self.fname)
        self.painter.repaint()

app = App()
app.run()
