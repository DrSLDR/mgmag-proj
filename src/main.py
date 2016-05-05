import sys, pygame
pygame.init()

size = width, height = 920, 840
speed = [1, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("/tmp/ball.gif")
ballrect = ball.get_rect()
from pgu import gui

app = gui.Desktop()
app.connect(gui.QUIT,app.quit,None)

c = gui.Table(width=200,height=120)

##::
class Quit(gui.Button):
    def __init__(self,**params):
        params['value'] = 'Quit'
        gui.Button.__init__(self,**params)
        self.connect(gui.CLICK,app.quit,None)
##

##Adding the button to the container.  By using the td method to add it, the button
##is placed in a sub-container, and it will not have to fill the whole cell.
##::
c.tr()
e = Quit()
c.td(e)
##

app.run(c)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
