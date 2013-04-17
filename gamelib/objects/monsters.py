import sys
import random
import math

from gamelib.objects import obj

ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Zombie(obj.GameObject):

    collide = obj.COL_AABB
    width = 20
    height = 43
    dampening = 0.90
    tex_index = 1
    tex_anchor = 2

    def __init__(self, x=32, y=32):
        super(Zombie, self).__init__(x, y)
        self.acc.y = -2000                
        
    def ai(self, player, map):
        delta = self.pos - player.pos
        self.face(1 if (self.pos - self.pos0).x < 0 else 0)
        if delta.magnitude_sq < 312*312:
            if delta.x > 0:
                self.acc.x = -random.randrange(500)
            else:
                self.acc.x = random.randrange(500)

            if random.random() < .1 and self.air == obj.ON_GROUND:
                self.pos0.y = self.pos.y - 12
        
    
class Robot(obj.GameObject):

    collide = obj.COL_AABB
    width = 24
    height = 39
    dampening = 0.90
    tex_index = 2
    tex_anchor = 4

    def __init__(self, x=32, y=32):
        super(Robot, self).__init__(x, y)
        self.acc.y = -2000                        
        
    def ai(self, player, map):
        delta = self.pos - player.pos
        self.face(1 if (self.pos - self.pos0).x < 0 else 0)

        if self.air == ON_GROUND and abs(delta.y) < 32:
            if delta.x > 0:
                self.acc.x = -1800
            else:
                self.acc.x = 1800
        else:
            self.acc.x = 0
        
    def collide(self, collisions):
        self.collisions = collisions
