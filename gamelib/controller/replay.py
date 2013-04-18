# from objects import player
import os
import time
import sys
import random
import array
import base64

from gamelib.controller import play
from gamelib import vector
from gamelib import map
from gamelib.objects import player

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet.window import key
    from pyglet import clock

class Replay(play.Game):
    """
    The Game class is THE MAN.
    """

    def __init__(self, dungeon, replay, window=None):
        
        self.window = window
        self.tick = 0        
        self.map = dungeon                            
        self.init_state(replay)

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

    def init_state(self, replay):
        super(Replay, self).init_state()        
        self.replay = replay
        # MULTI REPLAY SUPPORT
        # self.replay_archive.sort(key=lambda r: len(r), reverse=True)
        # self.ghosts = [player.Player(32, 32) for r in self.replay_archive[1:]]
        # self.replay = self.replay_archive[0]


    def sample_input(self):
        return self.replay[self.tick]

    def update(self, dt2):
        """
        Sample input, integrate game physics, and resolve collisions.
        """
        
        super(Replay, self).update(dt2)

        if self.tick >= len(self.replay):
            print 'Replay finished.'
            if not sys.modules.has_key('gamelib.controller.headless'):                            
                pyglet.clock.schedule_once(self.window.play, 0.0)
            print 'Player pos: ', self.player.pos
            print 'Player acc: ', self.player.acc    
            return 0
        else:
            return 1
            
    def on_key_press(self, symbol, modifiers):
        """
        Non-gameplay related keys.
        """
        if symbol == key.ESCAPE:
            pyglet.app.exit()
        elif symbol == key.TAB:
            pyglet.clock.schedule_once(self.window.edit, 0.0)
            self.map._highlight.enabled = True                    
        elif symbol == key.SPACE:
            pyglet.clock.schedule_once(self.window.play, 0.0)
