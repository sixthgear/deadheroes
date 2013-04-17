import sys
from collections import namedtuple, OrderedDict, defaultdict
from gamelib import vector
if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet import image

Point = namedtuple('Point', 'x y')

COL_AABB = 0x00
COL_CIRCLE = 0x01

if not sys.modules.has_key('gamelib.controller.headless'):
    # get an image sequence for all of the sprites
    sprites = image.ImageGrid(pyglet.resource.texture('sprites.png'), 8, 16).get_texture_sequence()
    for s in sprites:
        pass
    
class GameObject(object):

    tex = None

    def __init__(self, x, y):    
        
        self.pos = vector.Vec2d(x, y)
        self.pos0 = vector.Vec2d(x, y)
        self.acc = vector.Vec2d(0, 0)
        self.sprite = None
        self.tiles = set()
        
    def update(self, dt2):
        self.integrate(0, dt2)
        self.sprite.set_position(self.pos.x, self.pos.y)

    def integrate(self, t, dt2, dampening=1.0):
        """
        Perform Verlet integration
        """
        p = self.pos        
        self.pos = self.pos * (1.0 + dampening) - self.pos0 * dampening + self.acc * dt2
        # self.pos.x = self.pos.x * (1.0 + dampening) - self.pos0.x * dampening + self.acc.x * dt2
        # self.pos.y = self.pos.y * (1.0 + dampening) - self.pos0.y * dampening + self.acc.y * dt2
        self.pos0 = p