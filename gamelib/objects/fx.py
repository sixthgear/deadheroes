import sys

from gamelib.objects import obj

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *
    from pyglet import image
    from pyglet import sprite 

fx = []
_fx_sprite_batch = pyglet.graphics.Batch()

def cleanup():

    global fx, _fx_sprite_batch

    for f in fx:
        f.sprite.delete()
    fx = []
    _fx_sprite_batch = pyglet.graphics.Batch()


def spawn_fx(f):        
        fx.append(f)
        f.sprite.batch = _fx_sprite_batch

if not sys.modules.has_key('gamelib.controller.headless'):
    # get an image sequence for all of the sprites
    sprites = image.ImageGrid(pyglet.resource.texture('fx.png'), 4, 4).get_texture_sequence()
    for s in sprites:
        s.anchor_x = 64
        s.anchor_y = 64

class Explosion(object):

    def __init__(self, x, y):            

        self.alive = True
        self.life = 13
                
        frames = sprites[0:6]
        for f in frames:
            f.anchor_x = 64
            f.anchor_y = 64

        anim = image.Animation.from_image_sequence(frames, 0.03, loop=False)
        self.sprite = sprite.Sprite(anim, x=x, y=y)#, blend_src=GL_SRC_ALPHA, blend_dest=GL_ONE)
        # self.sprite.opacity = 128

