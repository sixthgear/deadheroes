import sys
import random
import math

from gamelib.objects import obj
from gamelib.objects import fx

class Zombie(obj.GameObject):

    tex_index       = 0x10
    width           = 18
    height          = 40
    dampening       = 0.90
    
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
    
    def collide_obj(self, o):
        o.die()
    
class Robot(obj.GameObject):
    
    tex_index       = 0x20
    width           = 18
    height          = 35
    dampening       = 0.90

    def __init__(self, x=32, y=32):
        super(Robot, self).__init__(x, y)
        self.acc.y = -2000                        
        
    def ai(self, player, map):
        delta = self.pos - player.pos 
        self.face(1 if (self.pos - self.pos0).x < 0 else 0)

        if self.air == obj.ON_GROUND and abs(delta.y) < 32:
            if delta.x > 0:
                self.acc.x = -1800
            else:
                self.acc.x = 1800
        else:
            self.acc.x *= 0.8
        
    def collide_obj(self, o):
        o.die()


class RocketLauncher(obj.GameObject):
    
    tex_index       = 0x30
    width           = 26
    height          = 36
    dampening       = 0.0
    
    def __init__(self, x=32, y=32):
        super(RocketLauncher, self).__init__(x, y)        
        self.rocket = None

    def ai(self, player, map):
        delta = self.pos - player.pos
            
        if not self.rocket and delta.magnitude_sq < 500*500:
            self.rocket = Rocket(self.pos.x+16, self.pos.y+16, self)
            self.rocket.acc = delta.normal * 500
            map.spawn_object(self.rocket)
    

    def rocket_death(self):        
        self.rocket = None


class Rocket(obj.GameObject):

    tex_index       = 0x31
    width           = 7
    height          = 7
    dampening       = 0.99
    
    def __init__(self, x=32, y=32, launcher=None):
        super(Rocket, self).__init__(x, y)
        self.launcher = launcher

    def die(self):
        fx.spawn_fx(fx.Explosion(self.pos.x, self.pos.y))
        self.alive = False

    def collide_obj(self, o):
        o.die()
        self.die()
        self.launcher.rocket_death()

    def collide_map(self, t):
        self.die()
        self.launcher.rocket_death()        

    def update(self, dt2):
        vel = (self.pos - self.pos0)
        self.sprite.rotation = vel.angle
        super(Rocket, self).update(dt2)

    def ai(self, player, map):
        delta = self.center - player.center
        self.acc = delta.normal * -400

