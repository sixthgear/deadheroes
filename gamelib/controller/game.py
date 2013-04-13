# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib.objects import slime


class Game(object):

    """
    The Game class is THE MAN.
    """

    def __init__(self, window):     
        self.window = window
        self.music = None        
        self.timer = clock.schedule_interval(self.update, 1/60.0)
        self.keys = key.KeyStateHandler()
        self.cursor = vector.Vec2d(0,0)
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1,0.05,0.0,1.0)

    def update(self, dt):
        dt = 1/30.0        

    def on_draw(self):      
        self.window.clear()        
        self.window.fps_display.draw()

    def on_mouse_motion(self, x, y, dx, dy): 
        self.cursor.x = x
        self.cursor.y = y

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_key_press(self, symbol, modifiers):
        
        if symbol == key.UP:
            pass
        elif symbol == key.DOWN:
            pass
        elif symbol == key.LEFT:
            pass
        elif symbol == key.RIGHT:
            pass

        if symbol == key.W:
            pass
        elif symbol == key.S:
            pass
        elif symbol == key.A:
            pass
        elif symbol == key.D:    
            pass

        if symbol == key.SPACE:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass 
            
    def on_mouse_release(self, x, y, button, modifiers):
        pass