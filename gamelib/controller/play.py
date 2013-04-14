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
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1,0.05,0.0,1.0)

    def update(self, dt):        
        # sample input        
        # record input
        # update
        self.map.update(self.dt)
        # collide
        # resolve        
    
    def on_draw(self):
        self.window.clear()
        self.map.draw()
        self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        if symbol == key.SPACE:
            pass
