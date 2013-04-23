import sys
import random
import math

from gamelib import vector
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

        if not player.alive:
            return

        delta = self.pos - player.pos
        self.face(1 if (self.pos - self.pos0).x < 0 else 0)
        if delta.magnitude_sq < 312*312 and self.has_los(player, map):
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

        if not player.alive:
            return

        delta = self.pos - player.pos 
        self.face(1 if (self.pos - self.pos0).x < 0 else 0)

        if self.air == obj.ON_GROUND and abs(delta.y) < 32 and self.has_los(player, map):
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
    width           = 24
    height          = 24
    tile_width      = 1
    tile_height     = 1
    dampening       = 0.0
    
    def __init__(self, x=32, y=32):
        super(RocketLauncher, self).__init__(x, y)        
        self.rocket = None

    def ai(self, player, map):

        if not player.alive:
            return

        if not self.rocket and self.has_los(player, map):
            delta = player.center - self.center
            self.rocket = Rocket(self.pos.x+16, self.pos.y+16, self, player)
            self.rocket.acc = delta.normal * 500
            map.spawn_object(self.rocket)
    
    def rocket_death(self):        
        self.rocket = None


class Rocket(obj.GameObject):

    tex_index       = 0x31
    width           = 7
    height          = 7
    dampening       = 0.95
    
    def __init__(self, x=32, y=32, launcher=None, player=None):
        super(Rocket, self).__init__(x, y)
        self.launcher = launcher
        self.player = player
        self.angle = (player.center - self.center).angle
        self.acc = vector.Vec2d(2000,0).rotated(self.angle)

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
        
        # print angle
        super(Rocket, self).update(dt2)
        vel = (self.pos - self.pos0)
        self.sprite.rotation = vel.angle        

    def ai_priority(self, player, map):

        if not player.alive:
            return

        vel = (self.pos - self.pos0)
        delta = (self.player.center - self.center)            
        rel_angle = (vel.x*delta.y) - (vel.y*delta.x);
        # dot = vel.normal.dot(delta.normal)
        # print rel_angle        
        if rel_angle < 0:
            self.angle += 20
            self.acc = vector.Vec2d(1000,0)
            self.acc.rotate(self.angle)
        else:
            self.angle -= 20
            self.acc = vector.Vec2d(1000,0)
            self.acc.rotate(self.angle)            

class Emitter(obj.GameObject):
    
    tex_index       = 0x32
    width           = 32
    height          = 32
    tile_width      = 1
    tile_height     = 1

