import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 


ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Player(obj.GameObject):

    collide = obj.COL_AABB
    width = 13
    height = 31
    
    def __init__(self, x=320, y=320):
        super(Player, self).__init__(x, y)
        self.acc.y =  -2000
        map.sprites[0].anchor_x = 16 - 13/2
        self.sprite = sprite.Sprite(map.sprites[0])
        
        self.air = FALLING
        self.jump_distance = 0


    def ground(self):
        self.air = ON_GROUND

    def jump(self):

        if self.air == ON_GROUND:
            self.pos.y += 4.0
            self.air = JUMPING
            self.jump_distance = 1.5
        elif self.air == JUMPING:
            vel = self.pos0 - self.pos
            if vel.y >= 0:
                self.air = FALLING
            else:
                self.pos.y += self.jump_distance
                self.jump_distance *= 0.95
        else:
            pass

    def update(self, dt2):

        self.integrate(0, dt2, dampening=0.90)
        self.sprite.set_position(self.pos.x, self.pos.y)
