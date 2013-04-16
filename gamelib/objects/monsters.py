import random
import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 


ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Zombie(obj.GameObject):

    collide = obj.COL_AABB
    width = 20
    height = 43
    
    def __init__(self, x=32, y=32):
        super(Zombie, self).__init__(x, y)
        self.acc.y = -2000
        obj.sprites[1].anchor_x = 7
        self.sprite = sprite.Sprite(obj.sprites[1])
        self.air = FALLING
        self.collisions = []
        
    def ground(self):
        self.air = ON_GROUND        

    def fall(self):
        if self.air == ON_GROUND:
            self.air = FALLING

    def jump(self):
        pass            

    def update(self, dt2):
        self.integrate(0, dt2, dampening=0.90)
        self.sprite.set_position(self.pos.x, self.pos.y)

    def ai(self, player, map):

        delta = self.pos - player.pos
        
        if delta.magnitude_sq < 312*312:
            if delta.x > 0:
                self.acc.x = -random.randrange(500)
            else:
                self.acc.x = random.randrange(500)

            if random.random() < .1 and self.air == ON_GROUND:
                self.pos0.y = self.pos.y - 12
        
    def collide(self, collisions):
        self.collisions = collisions