import sys
import math
from gamelib.objects import obj
from pyglet import image

KEY_LEFT            = 0x01
KEY_RIGHT           = 0x02
KEY_JUMP            = 0x04

class Player(obj.GameObject):
    
    tex_index       = 0x00
    width           = 12
    height          = 40
    dampening       = 0.9

    grace_jump_before = 10
    grace_jump_after = 5
    
    def __init__(self, x=32, y=32):
        super(Player, self).__init__(x, y)
        self.acc.y = -2000        
        self.air = obj.FALLING
        self.jump_distance = 0
        self.jump_timer = 0
        self.fall_timer = self.grace_jump_after
        self.jump_decay = 0.95
        self.jump_held = False

        frames = obj.sprites[0:16]
        for f in frames:
            f.anchor_y = self.height / 2
        self.animation = {}
        self.animation['idle'] = frames[0]
        self.animation['run'] = image.Animation.from_image_sequence(frames[1:13], 0.06)
        self.animation['jump'] = frames[14]
        self.animation['fall'] = frames[15]
        self.anim = self.animation['idle']
        self.sprite.image = self.anim        
        self.won = False

    def update(self, dt2):
        super(Player, self).update(dt2)

        if self.air == obj.ON_GROUND and abs(self.vel.x) < 2:
            if self.anim != self.animation['idle']:
                self.anim = self.animation['idle']
                self.sprite.image = self.anim.get_transform(flip_x=(self.facing==1))
                # self.face(self.facing)                
        elif self.air == obj.ON_GROUND:
            if self.anim != self.animation['run']:
                self.anim = self.animation['run']
                self.sprite.image = self.anim.get_transform(flip_x=(self.facing==1))
                # self.face(self.facing)
        elif self.air == obj.JUMPING:
            if self.anim != self.animation['jump']:
                self.anim = self.animation['jump']
                self.sprite.image = self.anim.get_transform(flip_x=(self.facing==1))
        elif self.air == obj.FALLING:
            self.fall_timer += 1
            if self.anim != self.animation['fall']:
                self.anim = self.animation['fall']
                self.sprite.image = self.anim.get_transform(flip_x=(self.facing==1))


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
            self.acc.x = self.vel.x * 500

        if controls & KEY_JUMP:

            # jump hit, on ground
            if self.air == obj.ON_GROUND and ((not self.jump_held) or self.jump_timer > 0):                
                self.jump()

            # grace jump
            elif self.air == obj.FALLING and not self.jump_held and self.fall_timer < self.grace_jump_after:
                self.jump()

            # jump held, add extra height
            elif self.air == obj.JUMPING and self.jump_held:
                
                if self.vel.y >= 0:
                    self.air = obj.FALLING
                    # print 'now falling'
                else:
                    self.pos.y += self.jump_distance
                    self.jump_distance *= self.jump_decay

            # give 5 ticks of grace time that jump can be hit before a platform is touched
            elif self.air == obj.FALLING and not self.jump_held and self.jump_timer == 0:
                self.jump_timer = self.grace_jump_before

            # jump held, haven't hit surface yet
            elif self.jump_held and self.jump_timer > 0:
                self.jump_timer -= 1            
            
            self.jump_held = True
        else:            
            if self.air == obj.JUMPING:
                self.air = obj.FALLING 
            self.jump_timer = 0
            self.jump_held = False


    def ground(self):
        self.air = obj.ON_GROUND        
        self.acc.y = 0
        self.fall_timer = 0

    def fall(self):
        if self.air == obj.ON_GROUND:
            self.air = obj.FALLING
            self.acc.y = -2000
            self.fall_timer = 0

    def jump(self):
        # print 'now jumping'        
        self.air = obj.JUMPING
        self.pos0.y = self.pos.y - 4.0
        self.acc.y = -2000
        self.jump_decay = 0.95
        self.jump_distance = 1.5
        self.jump_timer = 0
        self.fall_timer = self.grace_jump_after

