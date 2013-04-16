import random
import pyglet
import json
from gamelib import collide
from gamelib import vector
from pyglet.gl import *
from pyglet import image

# pixel size of a tile
MAP_TILESIZE = 32          

# edge flag constants
E_NONE              = 0x00
E_TOP               = 0x01
E_RIGHT             = 0x02
E_BOTTOM            = 0x04
E_LEFT              = 0x08
E_NOT_TOP           = ~E_TOP & 0xF
E_NOT_RIGHT         = ~E_RIGHT & 0xF
E_NOT_BOTTOM        = ~E_BOTTOM & 0xF
E_NOT_LEFT          = ~E_LEFT & 0xF
E_ALL               = 0x0F

# rotation constants
R_0                 = 0x00
R_90                = 0x03
R_180               = 0x02
R_270               = 0x01

# flip contants
FLIP_NONE           = 0x00
FLIP_HORIZ          = 0x01
FLIP_VERT           = 0x02
FLIP_BOTH           = 0x03

# tile type constants
T_EMPTY             = 0x00
T_BLOCK_WOOD        = 0x01
T_BLOCK_CONCRETE    = 0x02
T_BLOCK_STEEL       = 0x03
T_COLUMN            = 0x04
T_FLOOR             = 0x05
T_LADDER            = 0x06

# texture mutators for different edge congifurations.
# the first element of the tuple represents the texture index offset to add to the base index
# the second element of the tuple specifies if the texture should be rotated
TEX_MUT = {
    E_ALL:              (0,  R_0),
    E_NOT_RIGHT:        (16, R_0),
    E_NOT_BOTTOM:       (16, R_90),
    E_NOT_LEFT:         (16, R_180),
    E_NOT_TOP:          (16, R_270),
    E_TOP | E_BOTTOM:   (32, R_0),                    
    E_LEFT | E_RIGHT:   (32, R_270),
    E_LEFT | E_TOP:     (48, R_0),
    E_TOP | E_RIGHT:    (48, R_90),               
    E_RIGHT | E_BOTTOM: (48, R_180),
    E_BOTTOM | E_LEFT:  (48, R_270),               
    E_TOP:              (64, R_0),
    E_RIGHT:            (64, R_90),
    E_BOTTOM:           (64, R_180),
    E_LEFT:             (64, R_270),
    E_NONE:             (80, R_0),
}

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
        for y in range(self.height):
            for x in range(self.width):
                self.grid.append(Tile(x, y, type=T_EMPTY))

        for y in range(self.height):
            for x in range(self.width):
                tile = self.get(x, y)
                if self.is_bound(tile, E_ALL):
                    self.change(x, y, T_BLOCK_CONCRETE, force=True)

        # object data
        # these are all the game objects the maps needs to render over top of the tiles
        # this includes enemies, switches, wires, etc.
        self.objects = []

        # internal rendering data
        self._highlight = pyglet.graphics.vertex_list(4, 'v2f')
        self._highlight.enabled = False
        self._object_sprite_batch = pyglet.graphics.Batch()
        self._vertex_list = pyglet.graphics.vertex_list(0, 'v2f', 't2f')
        self._vertex_list_dirty = True    

    # tile lookup convience methods        
    def get(self, x, y): 
        return self.grid[y*self.width + x]
    def left(self, tile):
        return self.get(tile.x-1, tile.y)
    def right(self, tile):
        return self.get(tile.x+1, tile.y)
    def up(self, tile):
        return self.get(tile.x, tile.y+1)
    def down(self, tile):
        return self.get(tile.x, tile.y-1)
    
    def is_bound(self, tile, edge):        
        if edge & E_LEFT and tile.x == 0:
            return True
        if edge & E_BOTTOM and tile.y == 0:
            return True            
        if edge & E_RIGHT and tile.x == self.width - 1:
            return True
        if edge & E_TOP and tile.y == self.height - 1:
            return True            
        return False

    @classmethod
    def load(cls, map_id):
        """
        Loads a map from the server and returns a new Map obj.
        """
        with open ('mapdata.json', 'r') as f:             
            data = json.load(f)
            m = cls(data['width'], data['height'])
            for y in range(m.height):
                for x in range(m.width):
                    i = y * m.width + x
                    m.grid[i] = Tile(x, y, data['grid'][i], data['edges'][i])                    

        return m

    def save(self):
        """
        Writes a map to the server in JSON.
        """
        with open ('mapdata.json', 'w') as f: 
            jsondata = json.dumps({
                'width': self.width,
                'height': self.height,
                'grid': [t.type for t in self.grid],
                'edges': [t.edges for t in self.grid],
            })
            f.write(jsondata)
            
    def update(self, dt2):
        for o in self.objects:
            o.update(dt2)

    def change(self, x, y, type, force=False):
        """
        Modify the map and mark dirty so we rebuild the list.
        """
        tile = self.get(x,y)

        # can't change boundaries
        if not force and self.is_bound(tile, E_ALL):
            return

        # switch the tile edges if necessary
        if type != T_EMPTY and tile.type == T_EMPTY or type == T_EMPTY and tile.type != T_EMPTY:
            # the ol swaperoo
            tile.edges = ~tile.edges & 0XF
            
            # duplicate each edge to neighbor on the opposite side
            # top
            if not self.is_bound(tile, E_TOP):
                self.up(tile).edges = (self.up(tile).edges & E_NOT_BOTTOM) | ((tile.edges & E_TOP) << 2) 
            # right
            if not self.is_bound(tile, E_RIGHT):
                self.right(tile).edges = (self.right(tile).edges & E_NOT_LEFT) | ((tile.edges & E_RIGHT) << 2) 
            # bottom
            if not self.is_bound(tile, E_BOTTOM):
                self.down(tile).edges = (self.down(tile).edges & E_NOT_TOP) | ((tile.edges & E_BOTTOM) >> 2)
            # left
            if not self.is_bound(tile, E_LEFT):
                self.left(tile).edges = (self.left(tile).edges & E_NOT_RIGHT) | ((tile.edges & E_LEFT) >> 2) 

        # switch the tile type if necessary
        if tile.type != type:
            tile.type = type
            self._vertex_list_dirty = True


    def highlight(self, x, y):
        """
        Highlight a given tile location.
        """
        tile = self.get(x, y)

        # can't highlight boundaries
        if self.is_bound(tile, E_ALL):
            self._highlight.enabled = False
        else:
            self._highlight.vertices = tile.quad
            self._highlight.enabled = True

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
        if self._highlight.enabled:
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
                tile = self.get(x, y)

                if tile.type == T_EMPTY: 
                    # empty tile, so don't bother creating vertices
                    continue 

                # add vetices and tex coords for this tile
                vertices += tile.quad
                tex_coords += tile.tex(tile.type + TEX_MUT[tile.edges][0], TEX_MUT[tile.edges][1])
                
                # add corner decals on stacked tiles
                if not self.is_bound(tile, E_TOP | E_LEFT) and self.get(x-1, y+1).type == T_EMPTY and self.left(tile).edges & E_TOP and self.up(tile).edges & E_LEFT:
                    vertices += tile.quad
                    tex_coords += tile.tex(tile.type + 96, R_0)

                if not self.is_bound(tile, E_TOP | E_RIGHT) and self.get(x+1, y+1).type == T_EMPTY and self.right(tile).edges & E_TOP and self.up(tile).edges & E_RIGHT:
                    vertices += tile.quad
                    tex_coords += tile.tex(tile.type + 96, R_90)

                if not self.is_bound(tile, E_BOTTOM | E_RIGHT) and self.get(x+1, y-1).type == T_EMPTY and self.right(tile).edges & E_BOTTOM and self.down(tile).edges & E_RIGHT:
                    vertices += tile.quad
                    tex_coords += tile.tex(tile.type + 96, R_180)                    

                if not self.is_bound(tile, E_BOTTOM | E_LEFT) and self.get(x-1, y-1).type == T_EMPTY and self.left(tile).edges & E_BOTTOM and self.down(tile).edges & E_LEFT:
                    vertices += tile.quad
                    tex_coords += tile.tex(tile.type + 96, R_270)
                    
        self._vertex_list = pyglet.graphics.vertex_list(len(vertices)/2, 'v2f', 't2f')
        self._vertex_list.vertices = vertices
        self._vertex_list.tex_coords = tex_coords


    def collide(self, obj):
        """
        Collide one object against the map.
        """

        # assume this object is falling unless we resolve a ground collision
        obj.fall()

        # store a list of intersecting tiles to return
        collisions = []

        # determine a range of x,y tile indices to iterate through. For objects smaller than the size of
        # the grid, this will be at most 4 cells.        
        x0, y0 = int(obj.pos.x) / MAP_TILESIZE, int(obj.pos.y) / MAP_TILESIZE
        x1, y1 = int(obj.pos.x + obj.width) / MAP_TILESIZE + 1, int(obj.pos.y + obj.height) / MAP_TILESIZE + 1

        for y in range(y0, y1):
            for x in range(x0,x1):

                tile = self.get(x, y)
                tpos = vector.Vec2d(x*MAP_TILESIZE,y*MAP_TILESIZE)
            
                if tile.type == T_EMPTY:
                    continue

                elif collide.AABB_to_AABB(tpos, MAP_TILESIZE, MAP_TILESIZE, obj.pos, obj.width, obj.height):

                    # check for edge intersections
                    top = tile.edges & E_TOP and collide.AABB_to_AABB(
                        vector.Vec2d(tpos.x, tpos.y + MAP_TILESIZE), MAP_TILESIZE, 0, obj.pos, obj.width, obj.height)
                    bottom = tile.edges & E_BOTTOM and collide.AABB_to_AABB(
                        vector.Vec2d(tpos.x, tpos.y), MAP_TILESIZE, 0, obj.pos, obj.width, obj.height)
                    left = tile.edges & E_LEFT and collide.AABB_to_AABB(
                        vector.Vec2d(tpos.x, tpos.y), 0, MAP_TILESIZE, obj.pos, obj.width, obj.height)
                    right = tile.edges & E_RIGHT and collide.AABB_to_AABB(
                        vector.Vec2d(tpos.x+MAP_TILESIZE, tpos.y), 0, MAP_TILESIZE, obj.pos, obj.width, obj.height)

                    # keep track of the shortest projected edge for this tile.
                    # the resolution vector will typically be along the shortest axis of penetration.
                    projected_edge = (9999, 0x0)

                    # if we have an edge intersection and the project edge is smaller than what we've yet seen
                    if top and (tpos.y + MAP_TILESIZE) - obj.pos.y < projected_edge[0]:
                        projected_edge = ((tpos.y + MAP_TILESIZE) - obj.pos.y, E_TOP)
                    if right and (tpos.x + MAP_TILESIZE) - obj.pos.x < projected_edge[0]:
                        projected_edge =((tpos.x + MAP_TILESIZE) - obj.pos.x, E_RIGHT)
                    if bottom and (obj.pos.y + obj.height) - tpos.y < projected_edge[0]:
                        projected_edge = ((obj.pos.y + obj.height) - tpos.y, E_BOTTOM)
                    if left and (obj.pos.x + obj.width) - tpos.x < projected_edge[0]:
                        projected_edge = ((obj.pos.x + obj.width) - tpos.x, E_LEFT)
                
                    if projected_edge[1] != 0x0:
                        collisions.append(tile)

                    # calculate resolution
                    if projected_edge[1] == E_TOP:
                        obj.pos.y += projected_edge[0]                        
                        obj.ground()
                    elif projected_edge[1] == E_RIGHT:
                        obj.pos.x += projected_edge[0]                        
                    elif projected_edge[1] == E_BOTTOM:
                        obj.pos.y -= projected_edge[0]
                    elif projected_edge[1] == E_LEFT:
                        obj.pos.x -= projected_edge[0]
                        
        return collisions
        
class Tile(object):
    """
    A Tile is any given square of the map.
    """
    def __init__(self, x, y, type, edges=0):
        self.type = type
        self.objects = [] # references to objects contained here
        self.edges = edges
        self.x = x
        self.y = y

    def tex(self, index, rot, flip=0):
        tx0 = float(index % 16) / 16.0
        ty0 = float(index / 16) / 16.0
        tx1 = tx0 + 1.0 / 16.0
        ty1 = ty0 + 1.0 / 16.0
        tex_coords = [tx0, ty0, tx0, ty1, tx1, ty1, tx1, ty0]
        return tex_coords[rot*2:] + tex_coords[:rot*2]

    @property
    def quad(self):        
        return [
            self.x*MAP_TILESIZE, self.y*MAP_TILESIZE,
            self.x*MAP_TILESIZE, (self.y+1)*MAP_TILESIZE,
            (self.x+1)*MAP_TILESIZE, (self.y+1)*MAP_TILESIZE,
            (self.x+1)*MAP_TILESIZE, self.y*MAP_TILESIZE,
        ]

    def collide(self, obj):
        pass
