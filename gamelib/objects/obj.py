from collections import namedtuple, OrderedDict, defaultdict
from pyglet.gl import *
from gamelib import vector

Point = namedtuple('Point', 'x y')

class GameObject(object):

    tex = None

    def __init__(self, x, y):    
        self.loc = Point(x, y)        
        self.pos = vector.Vec2d(x, y)
        self.pos0 = vector.Vec2d(x, y)
        self.acc = vector.Vec2d(0, 0)
        self.sprite = None
        
    def update(self, dt):
        self.integrate(0, dt)
        self.sprite.set_position(self.pos.x, self.pos.y)

    def integrate(self, t, dt, dampening=1.0):
        """
        Perform Verlet integration
        """        
        dt2 = dt * dt
        p = self.pos
        self.pos = self.pos * (1.0 + dampening) - self.pos0 * dampening + self.acc * dt2
        self.pos0 = p