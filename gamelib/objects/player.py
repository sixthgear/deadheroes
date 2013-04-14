import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 

class Player(obj.GameObject):
    
    def __init__(self, x=320, y=320):
        super(Player, self).__init__(x, y)
        self.acc.y =  -4000
        self.sprite = sprite.Sprite(map.Map.sprites[0])
        self.jumping = True

    def jump(self):
        if self.jumping:
            return
        self.pos.y += 16.0
        self.jumping = True

    def update(self, dt):

        self.integrate(0, dt, dampening=0.90)

        if self.pos.y < 32:
            self.pos.y = 32
            self.jumping = False

        self.sprite.set_position(self.pos.x, self.pos.y)

    