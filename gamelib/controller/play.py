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
        self.replay_archive = []

        # use dungeon if passed into constructor, otherwise create a blank one
        if dungeon:
            self.map = dungeon
        else:
            self.map = map.Map(40, 25)
        
        self.init_state(0)
        self.init_gl()


    def init_state(self, replay=0):

        random.seed(0)
        self.tick = 0
        self.mode = replay

        if replay == 0:
            self.player = player.Player(32, 32)            
            self.replay = array.array('B')
            self.ghosts = []
        else:
            self.replay_archive.sort(key=lambda r: len(r), reverse=True)
            self.player = player.Player(32, 32)
            self.ghosts = [player.Player(32, 32) for r in self.replay_archive[1:]]
            self.replay = self.replay_archive[0]
        
        for t in self.map.grid:
            t.objects.clear()

        self.map.objects = []
    
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
        for r, p in enumerate([self.player] + self.ghosts):

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

                if self.tick >= len(self.replay_archive[r]) - 1:
                    if r == 0:
                        print 'Replay finished.'
                        self.mode = 0                        
                        pyglet.clock.schedule_once(self.window.edit, 0.0)
                        return
                    else:                        
                        continue

                key_int = self.replay_archive[r][self.tick]

            if key_int & KEY_LEFT:
                p.acc.x = -2000
                if p.air != player.ON_GROUND:
                    p.acc.x *= 0.75

            elif key_int & KEY_RIGHT:            
                p.acc.x = 2000
                if p.air != player.ON_GROUND:
                    p.acc.x *= 0.75                
            else:
                p.acc.x = 0

            if key_int & KEY_JUMP:
                p.jump()
            else:
                p.jump_release()        

            # integrate
            p.update(dt2)
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

        for g in self.ghosts:
            self.map.collide_geometry(g)


        for c in self.map.collide_objects(self.player):
            # pass
            # print 'player vs object', c
            if self.mode == 0:
                self.replay_archive.append(self.replay)
                pyglet.clock.schedule_once(self.init_state, 0.0)
            
            return

        

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
        for g in self.ghosts:
            g.sprite.draw()    
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

