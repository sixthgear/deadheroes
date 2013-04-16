import math
from gamelib.objects import obj
from gamelib import map
from pyglet import sprite 


ON_GROUND   = 0x00
JUMPING     = 0x01
FALLING     = 0x02

class Player(obj.GameObject):

    collide = obj.COL_AABB
    width = 20
    height = 43
    
    def __init__(self, x=32, y=32):
        super(Player, self).__init__(x, y)
        self.acc.y =  -2000
        obj.sprites[0].anchor_x = 7
        self.sprite = sprite.Sprite(obj.sprites[0])
        
        self.air = FALLING
        self.jump_distance = 0
        self.jump_timer = 0
        self.jump_held = False
        
    def ground(self):
        # if self.air != ON_GROUND: 
            # print 'on ground'
        self.air = ON_GROUND        

    def fall(self):
        if self.air == ON_GROUND:
            self.air = FALLING

    def jump(self):

        # jump hit, on ground
        if self.air == ON_GROUND and ((not self.jump_held) or self.jump_timer > 0):
            # print 'now jumping'
            self.air = JUMPING
            self.pos0.y = self.pos.y - 4.0            
            self.jump_distance = 1.5
            self.jump_timer = 0

        elif self.air == JUMPING and self.jump_held:
            vel = self.pos0 - self.pos
            if vel.y >= 0:
                self.air = FALLING
                # print 'now falling'
            else:
                self.pos.y += self.jump_distance
                self.jump_distance *= 0.95

        # give 10 ticks of grace time that jump can be hit before a platform is touched
        elif self.air == FALLING and not self.jump_held and self.jump_timer == 0:
            # print "jump timer set"
            self.jump_timer = 30

        elif self.jump_held and self.jump_timer > 0:
            self.jump_timer -= 1
            # print self.jump_timer

        else:
            pass
            # print 'what'

        self.jump_held = True


    def jump_release(self):
        self.jump_held = False        
        self.jump_timer = 0
        if self.air == JUMPING:
            self.air == FALLING

    def update(self, dt2):

        self.integrate(0, dt2, dampening=0.90)
        self.sprite.set_position(self.pos.x, self.pos.y)
