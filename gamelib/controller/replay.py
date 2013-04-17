# from objects import player
import os
import time
import sys
import random
import array
import base64

from gamelib import vector
from gamelib import map
from gamelib.objects import player

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet.window import key
    from pyglet import clock

class Replay(object):
    """
    The Game class is THE MAN.
    """

    def __init__(self, dungeon, replay, window=None):
        
        self.window = window
        self.tick = 0        
        self.map = dungeon
        self.replay = replay                        
        self.init_state()

        if not sys.modules.has_key('gamelib.controller.headless'):
            self.window = window
            self.music = None
            self.keys = key.KeyStateHandler()        
            self.init_gl()

    @classmethod
    def load(cls, filename, dungeon, window=None):

        with open (filename, 'r') as f:
            print 'Loading replay...'
            size = os.stat(filename)[6]
            r = array.array('B')
            r.fromstring(base64.b64decode(f.read()))
            return cls(dungeon=dungeon, replay=r, window=window)            

    def save(self):
        with open ('replay.rep', 'w') as f:
            print 'Saving replay (%d bytes, %d seconds)...' % (len(self.replay), len(self.replay) / 60)        
            f.write(base64.b64encode(self.replay.tostring()))
            print 'Success!'

    def init_state(self):

        random.seed(0)
        self.tick = 0        
        self.player = player.Player(32, 32)

        # MULTI REPLAY SUPPORT
        # self.replay_archive.sort(key=lambda r: len(r), reverse=True)
        # self.ghosts = [player.Player(32, 32) for r in self.replay_archive[1:]]
        # self.replay = self.replay_archive[0]

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
        
        controls = self.replay[self.tick]
   
        self.player.input(controls)
        # integrate
        self.player.update(dt2)
        
        for o in self.map.objects:
            o.update(dt2)

        if self.tick % 20 == 0:
            for o in self.map.objects:
                o.ai(self.player, self.map)

        self.collide()
        self.tick += 1

        if self.tick >= len(self.replay):
            print 'Replay finished.'
            if not sys.modules.has_key('gamelib.controller.headless'):                            
                pyglet.clock.schedule_once(self.window.play, 0.0)
            print 'Player pos: ', self.player.pos
            print 'Player acc: ', self.player.acc    
            return 0
        else:
            return 1
            

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

        # MULTI REPLAY SUPPORT
        # for g in self.ghosts:
        #     self.map.collide_geometry(g)

        for c in self.map.collide_objects(self.player):
            # player die
            # pyglet.clock.schedule_once(self.edit, 0.0)
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

        # MULTI REPLAY SUPPORT
        # for g in self.ghosts:
        #     g.sprite.draw()

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
        elif symbol == key.SPACE:
            pyglet.clock.schedule_once(self.window.play, 0.0)                       
