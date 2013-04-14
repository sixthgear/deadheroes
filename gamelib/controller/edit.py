# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib import map


class Game(object):

    """
    The Game class is THE MAN.
    """

    dt = 1/30.0

    def __init__(self, window):     
        self.window = window
        self.music = None        
        self.timer = clock.schedule_interval(self.update, 1/30.0)
        self.keys = key.KeyStateHandler()
        self.cursor = vector.Vec2d(0,0)        
        self.map = map.Map(40, 25)
        self.mode = 0
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1,0.05,0.0,1.0)

    def update(self, dt):
        pass
        # sample input        
        # record input
        # update
        # self.map.update(self.dt)
        # collide
        # resolve        
    
    def on_draw(self):
        self.window.clear()
        self.map.draw()
        self.window.fps_display.draw()

    def on_mouse_motion(self, x, y, dx, dy): 
        self.cursor.x = x
        self.cursor.y = y
        self.map.highlight(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)
        self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.mode)

    def on_key_press(self, symbol, modifiers):
        
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        if symbol == key.SPACE:
            pass
        if symbol == key._0:
            self.mode = 0
        if symbol == key._1:
            self.mode = 1
        if symbol == key._2:
            self.mode = 2
        if symbol == key._3:
            self.mode = 3

    def on_mouse_press(self, x, y, button, modifiers):
        pass 
            
    def on_mouse_release(self, x, y, button, modifiers):
        pass