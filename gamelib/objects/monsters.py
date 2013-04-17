import sys
import random
import math

from gamelib.objects import obj

ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Zombie(obj.GameObject):

    # collide = obj.COL_AABB
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
            self.acc.x *= 0.8
        
    def collide(self, collisions):
        pass


class RocketLauncher(obj.GameObject):

    # collide = obj.COL_AABB
    width = 26
    height = 36
    dampening = 0.0
    tex_index = 3
    tex_anchor = 0

    def __init__(self, x=32, y=32):
        super(RocketLauncher, self).__init__(x, y)        
        self.rocket = None

    def ai(self, player, map):
        delta = self.pos - player.pos
            
        if not self.rocket and delta.magnitude_sq < 500*500:
            self.rocket = Rocket(self.pos.x, self.pos.y, self)
            self.rocket.acc = delta.normal * 500
            map.spawn_object(self.rocket)
        
    def collide(self, collisions):
        pass

    def rocket_death(self):        
        self.rocket = None


class Rocket(obj.GameObject):

    # collide = obj.COL_AABB
    width = 9
    height = 9
    dampening = 0.99
    tex_index = 4
    tex_anchor = 0

    def __init__(self, x=32, y=32, launcher=None):
        super(Rocket, self).__init__(x, y)
        self.launcher = launcher
                
    def collide(self, collisions):
        self.alive = False
        self.launcher.rocket_death()

    def update(self, dt2):
        vel = (self.pos - self.pos0)
        self.sprite.rotation = vel.angle
        super(Rocket, self).update(dt2)

    def ai(self, player, map):
        delta = self.pos - player.pos
        self.acc = delta.normal * -560

