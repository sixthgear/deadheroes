import sys
from collections import namedtuple, OrderedDict, defaultdict
from gamelib import vector

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet import image
    from pyglet import sprite 

Point = namedtuple('Point', 'x y')

COL_AABB            = 0x00
COL_CIRCLE          = 0x01

ON_GROUND           = 0x00
JUMPING             = 0x01
FALLING             = 0x02

if not sys.modules.has_key('gamelib.controller.headless'):
    # get an image sequence for all of the sprites
    sprites = image.ImageGrid(pyglet.resource.texture('sprites.png'), 8, 16).get_texture_sequence()
    for s in sprites:
        s.anchor_x = 16
        s.anchor_y = 32
    
class GameObject(object):

    tex             = None
    tex_index       = 0x00
    width           = 0
    height          = 0
    tile_width      = 1
    tile_height     = 2            
    dampening       = 1.0

    def __init__(self, x, y):    
        
        self.pos = vector.Vec2d(x, y)
        self.pos0 = vector.Vec2d(x, y)
        self.acc = vector.Vec2d(0, 0)        
        self.facing = 0
        self.air = FALLING
        self.alive = True
        self.tiles = set()
        self.anim = None

        if not sys.modules.has_key('gamelib.controller.headless'):
            if self.tile_width == 1:
                self.sprite = sprite.Sprite(sprites[self.tex_index])
                self.sprite.image.anchor_x = self.width / 2 
                self.sprite.image.anchor_y = self.height / 2
                self.sprite.set_position(self.pos.x+ self.width/2, self.pos.y+self.height/2)
            else:
                # print type(sprites[self.tex_index])
                img = image.Texture.create(self.tile_width * 32, 64)
                for i in range(self.tile_width):
                    img.blit_into(sprites[self.tex_index + i].image_data, 32 * i, 0, 0)
                self.sprite = sprite.Sprite(img)
                self.sprite.image.anchor_x = self.width / 2 
                self.sprite.image.anchor_y = self.height / 2
                self.sprite.set_position(self.pos.x+ self.width/2, self.pos.y+self.height/2)

    @property
    def vel(self):
        return self.pos0 - self.pos

    @property
    def center(self):
        return self.pos + vector.Vec2d(self.width/2, self.height/2)

    def ground(self):
        self.air = ON_GROUND        
        self.acc.y = 0

    def fall(self):
        if self.air == ON_GROUND:
            self.air = FALLING
            self.acc.y = -2000

    def face(self, facing):        
        if facing != self.facing:
            self.facing = facing

            if self.anim:
                i = self.anim.get_transform(flip_x=(facing==1))
            else:
                i = sprites[self.tex_index].get_transform(flip_x=(facing==1))

            self.sprite.image = i

    def update(self, dt2):

        self.integrate(0, dt2, self.dampening)
        if not sys.modules.has_key('gamelib.controller.headless'):
            self.sprite.set_position(self.pos.x+ self.width/2, self.pos.y+self.height/2)
                
    def collide_obj(self, o):
        pass

    def collide_map(self, t):
        pass        

    def ai(self, map, player):
        pass

    def die(self):
        self.alive = False        

    def integrate(self, t, dt2, dampening=1.0):
        """
        Perform Verlet integration
        """
        # print self.pos0.y, self.pos.y, '(%f)' % self.acc.y, '->',
        p = self.pos
        self.pos = self.pos * (1.0 + dampening) - self.pos0 * dampening + self.acc * dt2        
        self.pos0 = p
        # print self.pos.y
