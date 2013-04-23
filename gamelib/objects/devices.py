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
        self.opened = False

    def open(self):
        self.get_sprite(2)
        self.opened = True

    def ai(self, player, map):
        if not [c for c in map.chests if not c.opened] and not self.opened:
            self.open()

    def collide_obj(self, o):
        if self.opened:
            self.won = True
    
class Chest(obj.GameObject):
    tex_index       = 0x78
    width           = 30
    height          = 27
    tile_width      = 1
    tile_height     = 1

    def __init__(self, *args, **kwargs):
        super(Chest, self).__init__(*args, **kwargs)
        self.opened = False

    def open(self):
        self.get_sprite(1)
        self.opened = True

    def collide_obj(self, o):
        if not self.opened:
            self.open()

class Anvil(obj.GameObject):
    tex_index       = 0x60
    width           = 32
    height          = 25
    tile_width      = 1
    tile_height     = 1

    def __init__(self, x, y):
        super(Anvil, self).__init__(x, y)
        self.acc.y = -2000

