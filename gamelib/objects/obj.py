from collections import namedtuple, OrderedDict, defaultdict
from pyglet.gl import *
from pyglet import sprite 
from gamelib import vector

class GameObject(object):

    tex = None

    def __init__(self, x, y):    

        # self.loc = Point(x, y)
        self.pos = vector.Vec2d(x, y)
        self.vel = vector.Vec2d(0, 0)
        self.acc = vector.Vec2d(0, 0)        
        self.sprite = None        
        
    def update(self, dt):
        pass
