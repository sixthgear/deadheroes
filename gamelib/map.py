import random

class Map(object):
    """
    The Map class holds a single multi-level dungeon.
    """

    def __init__(self, width, height):
        """
        Creates a new blank map.
        """
        self.id = 0             # the map id from the server
        self.width = width      # width of this map in tiles
        self.height = height    # height of this map in tiles
        self.deaths = 0         # the number of players to meet their demise here

        # grid data
        self.grid = [Tile(random.choice([T_EMPTY, T_BLOCK_WOOD])) for t in range(width * height)]

        # object data
        self.objects = []

        # internal rendering data
        self._vertex_list = None
        self._vertex_list_dirty = True

    def load(cls, map_id):
        """
        Loads a map from the server and returns a new Map object.
        """
        m = cls(48, 32)
        return m

    def save(self):
        """
        Writes a map to the server.
        """
        pass

    def draw(self):

        if self._vertex_list_dirty:
            # rebuild vertex list            

            # TEMP: write tile ids to console
            for y in range(self.height):
                for x in range(self.width):
                    print self.grid[y*self.width + x].type,
                print
            self._vertex_list_dirty = False

        # self._vertex_list.draw()
        

T_EMPTY             = 0x00
T_BLOCK_WOOD        = 0x01
T_BLOCK_CONCRETE    = 0x02
T_BLOCK_STEEL       = 0x03
T_COLUMN            = 0x04
T_FLOOR             = 0x05
T_LADDER            = 0x06

class Tile(object):
    """
    A Tile is any given square of the map.
    """
    def __init__(self, type):
        self.type = type