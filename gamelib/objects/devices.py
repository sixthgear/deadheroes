# from gamelib.util_hax import defer
from gamelib.objects import obj

class Door(obj.GameObject):
    tex_index       = 0x70
    width           = 54
    height          = 59
    tile_width      = 2
    tile_height     = 2

    def __init__(self, *args, **kwargs):
        super(Door, self).__init__(*args, **kwargs)
        self.won = False

    def collide_obj(self, o):
        if o.treasure_collected:
            self.won = True
    
class Chest(obj.GameObject):

    tex_index       = 0x72
    width           = 30
    height          = 27
    tile_width      = 1
    tile_height     = 1

    def collide_obj(self, o):
        self.sprite.image = obj.sprites[0x73]
        self.sprite.image.anchor_x = self.width / 2 
        self.sprite.image.anchor_y = self.height / 2
        self.sprite.set_position(self.pos.x+ self.width/2, self.pos.y+self.height/2)
        o.treasure_collected = True

class Anvil(obj.GameObject):
    tex_index       = 0x60
    width           = 32
    height          = 25
    tile_width      = 1
    tile_height     = 1

    def __init__(self, x, y):
        super(Anvil, self).__init__(x, y)
        self.acc.y = -2000