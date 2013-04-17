# from objects import player
import sys
import random
import array

from gamelib import vector
from gamelib import map
from gamelib.objects import player

from pyglet.gl import *
from pyglet.window import key
from pyglet import clock

KEY_LEFT            = 0x01
KEY_RIGHT           = 0x02
KEY_JUMP            = 0x04

class Game(object):

    """
    The Game class is THE MAN.
    """

    def __init__(self, dungeon, window=None):
                
        self.map = dungeon
        
        self.window = window
        self.music = None
        self.keys = key.KeyStateHandler()        
        self.init_gl()
                
        self.init_state()

    def init_state(self):

        random.seed(0)
        self.tick = 0
        self.player = player.Player(32, 32)            
        self.replay = array.array('B')
        
        for t in self.map.grid:
            t.objects.clear()

        self.map.objects = []
        self.map.spawn_objects()
        self.map.hash_object(self.player)


    def init_gl(self):
        """
        Set up initial OpenGL state.
        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1, 0.05, 0.0, 1.0)

    def update(self, dt2):
        """
        Sample input, integrate game physics, and resolve collisions.
        """
        # sample input
        controls = 0
        if self.keys[key.LEFT]:
            controls |= KEY_LEFT
        if self.keys[key.RIGHT]:
            controls |= KEY_RIGHT
        if self.keys[key.SPACE]:
            controls |= KEY_JUMP
        self.replay.append(controls)
        
        if controls & KEY_LEFT:
            self.player.acc.x = -2000
            if self.player.air != player.ON_GROUND:
                self.player.acc.x *= 0.75

        elif controls & KEY_RIGHT:            
            self.player.acc.x = 2000
            if self.player.air != player.ON_GROUND:
                self.player.acc.x *= 0.75                
        else:
            self.player.acc.x = 0

        if controls & KEY_JUMP:
            self.player.jump()
        else:
            self.player.jump_release()        

        # integrate
        self.player.update(dt2)
        # collisions = 
        

        for o in self.map.objects:
            o.update(dt2)

        if self.tick % 20 == 0:
            for o in self.map.objects:
                o.ai(self.player, self.map)

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

        self.map.collide_geometry(self.player)

        for c in self.map.collide_objects(self.player):
            pyglet.clock.schedule_once(self.window.replay, 0.0)
            return
        
        for o in self.map.objects:
            for c in self.map.collide_geometry(o):
                pass
                
        self.map.hash_object(self.player)

        for o in self.map.objects:            
            self.map.hash_object(o)
    
    def on_draw(self):
        """
        Draw the entire game state.
        """
        self.window.clear()
        self.map.draw()
        self.player.sprite.draw()        
        # self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        """
        Non-gameplay related keys.
        """
        if symbol == key.ESCAPE:            
            self.map.save()
            pyglet.app.exit()
        elif symbol == key.TAB:
            pyglet.clock.schedule_once(self.window.edit, 0.0)
            self.map._highlight.enabled = True
        