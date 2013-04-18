import sys
import math
from gamelib.objects import obj

KEY_LEFT            = 0x01
KEY_RIGHT           = 0x02
KEY_JUMP            = 0x04

class Player(obj.GameObject):
    
    tex_index       = 0x00
    width           = 20
    height          = 43
    dampening       = 0.9
    
    def __init__(self, x=32, y=32):
        super(Player, self).__init__(x, y)
        self.acc.y = -2000        
        self.air = obj.FALLING
        self.jump_distance = 0
        self.jump_timer = 0
        self.jump_held = False

    def input(self, controls):

        if controls & KEY_LEFT:
            self.face(1)
            self.acc.x = -2000
            if self.air != obj.ON_GROUND:
                self.acc.x *= 0.75

        elif controls & KEY_RIGHT:
            self.face(0)
            self.acc.x = 2000
            if self.air != obj.ON_GROUND:
                self.acc.x *= 0.75                
        else:
            self.acc.x = 0

        if controls & KEY_JUMP:
            self.jump()
        else:
            self.jump_release()        

    def jump(self):

        # jump hit, on ground
        if self.air == obj.ON_GROUND and ((not self.jump_held) or self.jump_timer > 0):
            # print 'now jumping'
            self.air = obj.JUMPING
            self.pos0.y = self.pos.y - 4.0
            self.acc.y = -2000
            self.jump_distance = 1.5
            self.jump_timer = 0

        elif self.air == obj.JUMPING and self.jump_held:
            vel = self.pos0 - self.pos
            if vel.y >= 0:
                self.air = obj.FALLING
                # print 'now falling'
            else:
                self.pos.y += self.jump_distance
                self.jump_distance *= 0.95

        # give 10 ticks of grace time that jump can be hit before a platform is touched
        elif self.air == obj.FALLING and not self.jump_held and self.jump_timer == 0:            
            self.jump_timer = 30

        elif self.jump_held and self.jump_timer > 0:
            self.jump_timer -= 1            
        else:
            pass            

        self.jump_held = True


    def jump_release(self):
        self.jump_held = False        
        self.jump_timer = 0
        if self.air == obj.JUMPING:
            self.air == obj.FALLING
