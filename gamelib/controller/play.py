# from objects import player
import sys
import random
import array

from gamelib import vector
from gamelib import map
from gamelib.objects import player
from gamelib.ui import hud_game

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet.window import key
    from pyglet import clock

class Game(object):
    """
    The Game class is THE MAN.
    """
    def __init__(self, dungeon, window=None):
                
        self.map = dungeon
        
        self.window = window
        self.music = None
        self.keys = key.KeyStateHandler()        
        self.hud = hud_game.HUD()
        self.init_gl()
                
        self.init_state()

    def init_state(self):

        random.seed(0)
        self.tick = 0
        
        self.replay = array.array('B')
        self.map.despawn_objects()        
        self.map.spawn_objects()
        self.map.spawn_player()

    def init_gl(self):
        """
        Set up initial OpenGL state.
        """
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.9,0.9,0.9,1.0)

    def sample_input(self):
        controls = 0
        if self.keys[key.LEFT]:
            controls |= player.KEY_LEFT
        if self.keys[key.RIGHT]:
            controls |= player.KEY_RIGHT
        if self.keys[key.SPACE]:
            controls |= player.KEY_JUMP
        self.replay.append(controls)
        return controls

    def update(self, dt2):
        """
        Sample input, integrate game physics, and resolve collisions.
        """
        # sample input

        if not self.map.player.alive:
            print 'DEAD!'
            pyglet.clock.schedule_once(self.window.edit, 0.0)
            return

        controls = self.sample_input()        
        self.map.player.input(controls)        
        self.map.player.update(dt2)
        
        for o in self.map.objects:
            o.update(dt2)

        if self.tick % 20 == 0:
            for o in self.map.objects:
                o.ai(self.map.player, self.map)

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

        self.map.collide_geometry(self.map.player)

        for c in self.map.collide_objects(self.map.player):
            c.collide_obj(self.map.player)
        
        for o in self.map.objects:
            for c in self.map.collide_geometry(o):
                o.collide_map(c)
                
        self.map.hash_object(self.map.player)

        for o in self.map.objects:            
            self.map.hash_object(o)

        for o in [o for o in self.map.objects if not o.alive]:
            self.map.despawn_object(o)

        self.map.objects = [o for o in self.map.objects if o.alive]
    
    def on_draw(self):
        """
        Draw the entire game state.
        """
        self.window.clear()
        self.map.draw()
        self.map.player.sprite.draw()
        self.hud.draw()
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
        