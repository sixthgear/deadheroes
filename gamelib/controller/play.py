# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib import map
from gamelib.objects import player

class Game(object):

    """
    The Game class is THE MAN.
    """

    def __init__(self, window, dungeon=None):
        self.window = window
        self.music = None                        
        self.keys = key.KeyStateHandler()        
        self.player = player.Player()
        self.tick = 0
        # use dungeon if passed into constructor, otherwise create a blank one
        if dungeon:
            self.map = dungeon
        else:
            self.map = map.Map(40, 25)

        self.init_gl()

    def init_gl(self):
        """
        Set up initial OpenGL state.
        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1, 0.05, 0.0, 1.0)

    def update(self, dt):
        """
        Sample input, integrate game physics, and resolve collisions.
        """
        # sample input
        if self.keys[key.LEFT]:
            self.player.acc.x = -2000
        elif self.keys[key.RIGHT]:
            self.player.acc.x = 2000
        else:
            self.player.acc.x = 0
        if self.keys[key.SPACE]:
            self.player.jump()
        elif self.player.air == player.JUMPING:
            self.player.air = player.FALLING

        # record input for this frame

        # integrate
        self.player.update(dt)
        self.map.update(dt)
        self.collide()
        self.tick += 1

    def collide(self):
        """
        Perform all collision checks we need for this frame.
        - collide player against 6 possible intersecting map tiles
        - collide other objects against each 6 possible intersecting map tiles
        
        + - - + - - +
        | 1+-----+2 |
        + -|     |- +
        | 3|  P  |4 |
        + -|     |- +
        | 5+-----+6 |
        + - - + - - +

        - collide player against any objects hashed in the area
        - resolve        
        """

        collisions = self.map.collide(self.player)
        for t in collisions:
            pass
            # self.map.change(x,y,T_BLOCK_CONCRETE)
            # print collisions
    
    def on_draw(self):
        """
        Draw the entire game state.
        """
        self.window.clear()
        self.map.draw()
        self.player.sprite.draw()
        self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        """
        Non-gameplay related keys.
        """
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        if symbol == key.TAB:            
            pyglet.clock.schedule_once(self.window.edit, 0.0)        
