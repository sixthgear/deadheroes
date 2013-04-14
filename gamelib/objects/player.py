import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 

class Player(obj.GameObject):
    
    def __init__(self, x=320, y=320):
        super(Player, self).__init__(x, y)
        self.sprite = sprite.Sprite(map.Map.sprites[0])
        self.acc.y = -2000
        self.jumping = True

    def jump(self):
        if self.jumping:
            return
        self.vel.y = 540
        self.jumping = True

    def update(self, dt):

        self.vel += self.acc * dt
        self.pos += self.vel * dt

        if self.pos.y < 32:
            self.pos.y = 32
            self.jumping = False

        self.sprite.set_position(self.pos.x, self.pos.y)