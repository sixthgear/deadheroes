import random
import pyglet
from pyglet.gl import *

MAP_TILESIZE = 32          # pixel size of a tile

class Map(object):
    """
    The Map class holds a single multi-level dungeon.
    """

    tex = pyglet.resource.texture('sprites.png')

    def __init__(self, width, height):
        """
        Creates a new blank map.
        """
        self.id = 0             # the map id from the server
        self.width = width      # width of this map in tiles
        self.height = height    # height of this map in tiles
        self.deaths = 0         # the number of players to meet their demise here

        # grid data
        self.grid = []
        for i in range(width * height):
            if i / width in [0, height-1] or i % width in [0, width-1]:
                t = 1
            else:
                t = random.choice((0,0,0,0,0,0,0,0,0,0,0,0,2,3))
            self.grid.append(Tile(type=t))

        # object data
        # these are all the game objects the maps needs to render over top of the tiles
        # this includes enemies, switches, wires, etc.
        self.objects = []

        # internal rendering data
        self._highlight = pyglet.graphics.vertex_list(4, 'v2f')
        self._object_sprite_batch = pyglet.graphics.Batch()
        self._vertex_list = pyglet.graphics.vertex_list(0, 'v2f', 't2f')
        self._vertex_list_dirty = True

    def load(cls, map_id):
        """
        Loads a map from the server and returns a new Map object.
        """
        m = cls(48, 32)
        return m

    def save(self):
        """
        Writes a map to the server in JSON.
        """
        pass

    def get(self, x, y):
        """
        Returns tile at position x, y
        """
        return self.grid[y*self.width + x]

    def update(self, dt):
        pass

    def change(self, x, y, t):
        self.get(x,y).type = t
        self._vertex_list_dirty = True

    def highlight(self, x, y):
        self._highlight.vertices = [
            x*MAP_TILESIZE, y*MAP_TILESIZE,
            x*MAP_TILESIZE, (y+1)*MAP_TILESIZE,
            (x+1)*MAP_TILESIZE, (y+1)*MAP_TILESIZE,
            (x+1)*MAP_TILESIZE, y*MAP_TILESIZE,
        ]

    def draw(self):
        """
        Render the current map, checking if the vertex list has been dirtied and needs to be rebuilt.
        """

        # check if we need to rebuild the vertex list. We defer this until drawing time so that 
        # every operation that modifies the map doesn't need to rebuild this list every time.
        if self._vertex_list_dirty:
            self.rebuild_vertices()
            self._vertex_list_dirty = False

        # bind the tile texture and draw the whole map
        glEnable(GL_TEXTURE_2D)
        glBindTexture(self.tex.target, self.tex.id)
        self._vertex_list.draw(GL_QUADS)

        # draw the objects batch
        self._object_sprite_batch.draw()

        glDisable(GL_TEXTURE_2D)
        glColor4f(1,1,1,.5)
        self._highlight.draw(GL_QUADS)
        glColor4f(1,1,1,1)


    def rebuild_vertices(self):

        self._vertex_list.delete()        
        vertices = []
        tex_coords = []

        for y in range(self.height):
            for x in range(self.width):

                tile = self.get(x, y).type

                if tile == T_EMPTY: # empty tile, so don't bother creating vertices
                    continue 

                vertices += [
                    x*MAP_TILESIZE, y*MAP_TILESIZE,
                    x*MAP_TILESIZE, (y+1)*MAP_TILESIZE,
                    (x+1)*MAP_TILESIZE, (y+1)*MAP_TILESIZE,
                    (x+1)*MAP_TILESIZE, y*MAP_TILESIZE,
                ]
                
                tx0 = float(tile % 16) / 16.0
                ty0 = float(tile / 16) / 16.0
                tx1 = tx0 + 1.0 / 16.0
                ty1 = ty0 + 1.0 / 16.0
                tex_coords += [tx0, ty0, tx0, ty1, tx1, ty1, tx1, ty0]

        self._vertex_list = pyglet.graphics.vertex_list(len(vertices)/2, 'v2f', 't2f')
        self._vertex_list.vertices = vertices
        self._vertex_list.tex_coords = tex_coords
        
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