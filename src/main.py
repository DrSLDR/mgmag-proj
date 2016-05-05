import sys, pygame
from pgu import gui

class UserInterface(gui.Desktop):
    def __init__(self,display):
        from dialogs import HelpDialog, QuitDialog, WelcomeDialog
        gui.Desktop.__init__(self)

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

class GameEngine(object):
    def __init__(self, disp):
        self.disp = disp
        self.app = UserInterface(self.disp)
        self.app.engine = self

        self.logo = pygame.image.load(Logo.game)
        self.ballrect = self.logo.get_rect()

    # Pause the game clock
    def pause(self):
        self.clock.pause()

    # Resume the game clock
    def resume(self):
        self.clock.resume()

    def render(self, dest, rect):
        size = width, height = 920, 840
        speed = [1, 2]
        self.ballrect = self.ballrect.move(speed)
        if self.ballrect.left < 0 or self.ballrect.right > width:
            speed[0] = -speed[0]
        if self.ballrect.top < 0 or self.ballrect.bottom > height:
            speed[1] = -speed[1]

        black = 0, 0, 255 # which is blue
        dest.fill(black)
        # YOU JUST GOT RECT!
        dest.blit(self.cuzco, self.ballrect)

        def draw_clock(name, pt, radius, col, angle):
            pygame.draw.circle(dest, col, pt, radius)
            pygame.draw.line(dest, (0,0,0), pt, 
                             (pt[0]+radius*math.cos(angle),
                              pt[1]+radius*math.sin(angle)), 2)
            tmp = self.font.render(name, True, (255,255,255))
            dest.blit(tmp, (pt[0]-radius, pt[1]+radius+5))

        # Draw the real time clock
        angle = self.clock.get_real_time()*2*math.pi/10.0
        draw_clock("Real time", (30,30), 25, (255,200,100), angle)

        # Now draw the game clock
        angle = self.clock.get_time()*2*math.pi/10.0
        draw_clock("Game time", (90,30), 25, (255,100,255), angle)

        return (rect,)

    def run(self):
        self.app.update()
        pygame.display.flip()

        self.font = pygame.font.SysFont("", 16)

        self.clock = timer.Clock() #pygame.time.Clock()
        done = False
        while not done:
            # Process events
            for ev in pygame.event.get():
                if (ev.type == pygame.QUIT or 
                    ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    done = True
                else:
                    # Pass the event off to pgu
                    self.app.event(ev)
            # Render the game
            rect = self.app.get_render_area()
            updates = []
            self.disp.set_clip(rect)
            lst = self.render(self.disp, rect)
            if (lst):
                updates += lst
            self.disp.set_clip()

            # Cap it at 30fps
            self.clock.tick(30)

            # Give pgu a chance to update the display
            lst = self.app.update()
            if (lst):
                updates += lst
            pygame.display.update(updates)
            pygame.time.wait(10)

disp = pygame.display.set_mode((800, 600))
eng = GameEngine(disp)
eng.run()
