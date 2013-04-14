import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 


ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Player(obj.GameObject):
    
    def __init__(self, x=320, y=320):
        super(Player, self).__init__(x, y)
        self.acc.y =  -2000
        self.sprite = sprite.Sprite(map.Map.sprites[0])
        self.air = FALLING
        self.jump_distance = 0

    def jump(self):

        if self.air == ON_GROUND:
            self.pos.y += 4.0
            self.air = JUMPING
            self.jump_distance = 1.4
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

        if self.pos.y < 32:
            self.pos0.y = 32
            self.pos.y = 32
            self.air = ON_GROUND

        self.sprite.set_position(self.pos.x, self.pos.y)
