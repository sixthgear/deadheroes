import random
import pyglet

from gamelib import collide
from gamelib import vector
from pyglet.gl import *
from pyglet import image

MAP_TILESIZE = 32          # pixel size of a tile


sprites = image.ImageGrid(pyglet.resource.texture('sprites.png'), 8, 16).get_texture_sequence()
for s in sprites:
    pass
    # s.anchor_x = 16

class Map(object):
    """
    The Map class holds a single multi-level dungeon.
    """

    tiles_tex = pyglet.resource.texture('tiles.png')
    

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
        for i in range(self.width * self.height):
            self.grid.append(Tile(type=T_EMPTY))

        print len(self.grid)

        for y in range(self.height):
            for x in range(self.width):                
                if y in [0, height-1] or x in [0, width-1]:
                    self.change(x, y, T_BLOCK_WOOD)
                
            
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

    def update(self, dt2):
        for o in self.objects:
            o.update(dt2)

    def change(self, x, y, t):
        """
        Modify the map and mark dirty so we rebuild the list.
        """
        old = self.get(x,y)
        if old.type != t:

            # swap edge flags
            old.edge_flags = ~old.edge_flags & 0XF
            # print old.edge_flags, self.get(x-1, y).edge_flags
            # duplicate each edge to neighbor on the opposite side
            if y < self.height-1:
                self.get(x, y+1).edge_flags = (self.get(x, y+1).edge_flags & 0xB) | ((old.edge_flags & 0x1) << 2) #   top
            else:
                old.edge_flags &= 0xE

            if x < self.width-1:
                self.get(x+1, y).edge_flags = (self.get(x+1, y).edge_flags & 0x7) | ((old.edge_flags & 0x2) << 2) #   right
            else:
                old.edge_flags &= 0xD

            if y > 0:
                self.get(x, y-1).edge_flags = (self.get(x, y-1).edge_flags & 0xE) | ((old.edge_flags & 0x4) >> 2) #   bottom
            else:
                old.edge_flags &= 0xB

            if x > 0:
                self.get(x-1, y).edge_flags = (self.get(x-1, y).edge_flags & 0xD) | ((old.edge_flags & 0x8) >> 2) #   left
            else:
                old.edge_flags &= 0x7

            # print self.get(x-1, y).edge_flags
            old.type = t
            self._vertex_list_dirty = True

    def highlight(self, x, y):
        """
        Highlight a given tile location.
        """
        t = self.get(x, y)
        print x, y, t.edge_flags
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
        glBindTexture(self.tiles_tex.target, self.tiles_tex.id)
        self._vertex_list.draw(GL_QUADS)

        # draw the objects batch
        self._object_sprite_batch.draw()

        # draw the highlight square
        glDisable(GL_TEXTURE_2D)
        glColor4f(1,1,1,.5)
        self._highlight.draw(GL_QUADS)
        glColor4f(1,1,1,1)

    def rebuild_vertices(self):
        """
        Cycle through our map data and build a grid of quads with correct texcoords. This will be used
        to render the map.
        """        
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


    def collide(self, object):

        collisions = []
        x0, y0 = int(object.pos.x) / MAP_TILESIZE, int(object.pos.y) / MAP_TILESIZE
        x1, y1 = int(object.pos.x + object.width) / MAP_TILESIZE + 1, int(object.pos.y + object.height) / MAP_TILESIZE + 1

        edges = []

        for y in range(y0, y1):
            for x in range(x0,x1):

                tile = self.get(x, y)
                tpos = vector.Vec2d(x*MAP_TILESIZE,y*MAP_TILESIZE)
                if tile.type == T_EMPTY:
                    continue
                else:
                    if collide.AABB_to_AABB(tpos, MAP_TILESIZE, MAP_TILESIZE, object.pos, object.width, object.height):
                        
                        if tile.edge_flags & 0x1:
                            edges.append(((tpos.y + MAP_TILESIZE) - object.pos.y, 0x1))
                        if tile.edge_flags & 0x2:
                            edges.append(((tpos.x + MAP_TILESIZE) - object.pos.x, 0x2))
                        if tile.edge_flags & 0x4:
                            edges.append(((object.pos.y + object.height) - tpos.y, 0x4))
                        if tile.edge_flags & 0x8:
                            edges.append(((object.pos.x + object.width) - tpos.x, 0x8))
                                            
                        if edges:    
                            # calculate resolution
                            projected_edge = sorted(edges)[0]

                            if projected_edge[1] == 0x1:
                                object.pos.y += projected_edge[0]
                                object.pos0.y = object.pos.y
                                object.ground()                                
                            if projected_edge[1] == 0x2:
                                object.pos.x += projected_edge[0]
                                object.pos0.x = object.pos.x
                                object.acc.x = 0
                            if projected_edge[1] == 0x4:
                                object.pos.y -= projected_edge[0]
                                object.pos0.y = object.pos.y
                            if projected_edge[1] == 0x8:
                                object.pos.x -= projected_edge[0]
                                object.pos0.x = object.pos.x                                
                                object.acc.x = 0


                            # object.pos0.x = object.pos.x
                            # object.pos0.y = object.pos.y
                            collisions.append((object, tile))

        return collisions
        #self.get(x,y).collide(obj)
        
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
        self.objects = [] # references to objects contained here
        self.edge_flags = 0x0000

    def collide(self, obj):
        pass
