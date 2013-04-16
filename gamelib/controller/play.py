# from objects import player
import random
import array
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib import map
from gamelib.objects import player
from gamelib.objects import monsters

KEY_LEFT            = 0x01
KEY_RIGHT           = 0x02
KEY_JUMP            = 0x04

class Game(object):

    """
    The Game class is THE MAN.
    """

    def __init__(self, window, dungeon=None):
        self.window = window
        self.music = None                        
        self.keys = key.KeyStateHandler()        
        
        self.tick = 0
        self.replay = array.array('B')

        # use dungeon if passed into constructor, otherwise create a blank one
        if dungeon:
            self.map = dungeon
        else:
            self.map = map.Map(40, 25)
        
        self.init_state(0)
        self.init_gl()


    def init_state(self, replay):

        self.tick = 0
        self.player = player.Player(32, 32)
        self.map.objects = []
        [t.objects.clear() for t in self.map.grid]
        self.mode = replay
        if replay == 0:
            self.replay = array.array('B')

        random.seed(0)

        for i in range(20):
            p = random.randrange(40), random.randrange(25)            
            tile = self.map.get(*p)
            if tile.is_empty and self.map.up(tile).is_empty:
                z = monsters.Zombie(p[0]*map.MAP_TILESIZE,p[1]*map.MAP_TILESIZE)
                z.sprite.batch = self.map._object_sprite_batch
                self.map.objects.append(z)
                self.map.hash_object(z)

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

        key_int = 0
        if self.mode == 0:
            if self.keys[key.LEFT]:
                key_int |= KEY_LEFT
            if self.keys[key.RIGHT]:
                key_int |= KEY_RIGHT
            if self.keys[key.SPACE]:
                key_int |= KEY_JUMP
            self.replay.append(key_int)
        else:
            key_int = self.replay[self.tick]
            if self.tick == len(self.replay)-1:
                print 'Replay finished.'
                self.mode = 0

        if key_int & KEY_LEFT:
            self.player.acc.x = -2000
            if self.player.air != player.ON_GROUND:
                self.player.acc.x *= 0.75

        elif key_int & KEY_RIGHT:            
            self.player.acc.x = 2000
            if self.player.air != player.ON_GROUND:
                self.player.acc.x *= 0.75                
        else:
            self.player.acc.x = 0

        if key_int & KEY_JUMP:
            self.player.jump()
        else:
            self.player.jump_release()        

        # integrate
        self.player.update(dt2)
        # self.map.update(dt)
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

        # collisions = 
        for c in self.map.collide_geometry(self.player):
            pass
            # print 'player vs map', c

        for c in self.map.collide_objects(self.player):
            # pass
            # print 'player vs object', c
            self.init_state(0)

        

        # if collisions:
        #     print collisions

        for o in self.map.objects:
            for c in self.map.collide_geometry(o):
                pass
                # print 'object vs map', c
            # o.collide(collisions)

        # for t in collisions:
        #     pass
            # self.map.change(x,y,T_BLOCK_CONCRETE)
            # print collisions
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
        elif symbol == key.R:
            print 'Playing replay (%d bytes, %d seconds)...' % (len(self.replay), len(self.replay) / 60)
            self.init_state(1)

