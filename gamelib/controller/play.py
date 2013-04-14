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
        self.cursor = vector.Vec2d(0,0)
        if dungeon:
            self.map = dungeon
        else:
            self.map = map.Map(40, 25)
        self.player = player.Player()
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1,0.05,0.0,1.0)

    def update(self, dt):
        # sample input
        if self.keys[key.LEFT]:
            self.player.pos.x -= 0.75
        elif self.keys[key.RIGHT]:
            self.player.pos.x += 0.75
        if self.keys[key.SPACE]:
            self.player.jump()


        # record input

        # update
        self.player.update(dt)
        self.map.update(dt)

        # collide
        # resolve
    
    def on_draw(self):
        self.window.clear()
        self.map.draw()
        self.player.sprite.draw()
        self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        
        if symbol == key.ESCAPE:            
            pyglet.clock.schedule_once(self.window.edit, 0.0)
        if symbol == key.SPACE:
            pass
