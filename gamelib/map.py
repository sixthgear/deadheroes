import sys
import random
import pyglet
import json
import requests

from gamelib import collide
from gamelib import vector
from gamelib.objects.info import *
from gamelib.objects import fx

# from gamelib.objects import monsters

if not sys.modules.has_key('gamelib.controller.headless'):
    from pyglet.gl import *

# pixel size of a tile
MAP_TILESIZE = 32

# edge flag constants
E_NONE                      = 0x00
E_TOP                       = 0x01
E_RIGHT                     = 0x02
E_BOTTOM                    = 0x04
E_LEFT                      = 0x08
E_NOT_TOP                   = ~E_TOP & 0xF
E_NOT_RIGHT                 = ~E_RIGHT & 0xF
E_NOT_BOTTOM                = ~E_BOTTOM & 0xF
E_NOT_LEFT                  = ~E_LEFT & 0xF
E_ALL                       = 0x0F

# rotation constants
R_0                         = 0x00
R_90                        = 0x03
R_180                       = 0x02
R_270                       = 0x01

# flip contants
FLIP_NONE                   = 0x00
FLIP_HORZ                   = 0x01
FLIP_VERT                   = 0x02
FLIP_BOTH                   = 0x03

# tile type constants
T_EMPTY                     = 0x00
T_BLOCK_WOOD                = 0x01
T_BLOCK_CONCRETE            = 0x02
T_BLOCK_STEEL               = 0x03
T_SPIKES                    = 0x04
T_LAVA                      = 0x05

TILE_INFO = {
    T_EMPTY:                (0,),
    T_BLOCK_WOOD:           (10,),
    T_BLOCK_CONCRETE:       (20,),
    T_BLOCK_STEEL:          (30,),
    T_SPIKES:               (50,),
    T_LAVA:                 (100,),
}

# texture mutators for different edge congifurations.
# the first element of the tuple represents the texture index offset to add to the base index
# the second element of the tuple specifies if the texture should be rotated
TEX_MUT = {
    E_ALL:                  (0,  R_0),
    E_NOT_RIGHT:            (16, R_0),
    E_NOT_BOTTOM:           (16, R_90),
    E_NOT_LEFT:             (16, R_180),
    E_NOT_TOP:              (16, R_270),
    E_TOP | E_BOTTOM:       (32, R_0),
    E_LEFT | E_RIGHT:       (32, R_270),
    E_LEFT | E_TOP:         (48, R_0),
    E_TOP | E_RIGHT:        (48, R_90),
    E_RIGHT | E_BOTTOM:     (48, R_180),
    E_BOTTOM | E_LEFT:      (48, R_270),
    E_TOP:                  (64, R_0),
    E_RIGHT:                (64, R_90),
    E_BOTTOM:               (64, R_180),
    E_LEFT:                 (64, R_270),
    E_NONE:                 (80, R_0),
}

class Chunk(object):
    """
    A Chunk is a 4x4 grid that can be used to generate a random dungeon.
    """
    def __init__(self, width, height, name=''):
        """
        Creates a new blank map.
        """
        self.width = width      # width of this map in tiles
        self.height = height    # height of this map in tiles

        # create grid
        self.grid = [Tile(t%width, t/width, type=T_EMPTY) for t in range(width*height)]



class Map(object):
    """
    The Map class holds a single multi-level dungeon.
    """

    tiles_tex = pyglet.resource.texture('tiles.png')

    def __init__(self, width, height, name=''):
        """
        Creates a new blank map.
        """
        self.dungeon_id = ''    # the map id from the server
        self.name = name        # the name of the dungeoneer who created this
        self.width = width      # width of this map in tiles
        self.height = height    # height of this map in tiles
        self.deaths = 0         # the number of players to meet their demise here
        self.pending_budget = 0


        # chunks
        self.chunks = []

        # create grid
        self.grid = [Tile(t%width, t/width, type=T_EMPTY) for t in range(width*height) ]

        # live object data
        # these are all the game objects the maps needs to render over top of the tiles
        # this includes enemies, switches, wires, etc.
        self.player = None
        self.objects = []
        self.object_spawn_list = {76: CHEST, 42: DOOR}
        self.player_spawn = 42
        self.doors = []

        # create edges
        for tile in self.grid:
            if self.is_bound(tile, E_ALL):
                self.change(tile.x, tile.y, T_BLOCK_CONCRETE, force=True)

        if not sys.modules.has_key('gamelib.controller.headless'):
            # internal rendering data
            self._highlight = pyglet.graphics.vertex_list(4, 'v2f')
            self._highlight.enabled = False
            self._object_sprite_batch = pyglet.graphics.Batch()
            self._vertex_list = pyglet.graphics.vertex_list(0, 'v2f', 't2f')
            self._vertex_list_dirty = True

        self.init_state()

    def init_state(self):
        self._highlight.enabled = True
        self.despawn_objects()
        self._object_sprite_batch = pyglet.graphics.Batch()
        self.spawn_objects()
        self.spawn_player()
        self.doors = []
        self.chests = []

        for o in self.objects:
            if o.__class__ == INFO[DOOR].cls:
                self.doors.append(o)

        for o in self.objects:
            if o.__class__ == INFO[CHEST].cls:
                self.chests.append(o)

    @classmethod
    def load(cls, dungeon_id, name, data):
        """
        Loads a map from the server and returns a new Map obj.
        """
        # with open ('mapdata.json', 'r') as f:
            # data = json.load(f)
        # print data
        # data = json.loads(data)
        m = cls(data['width'], data['height'])
        m.dungeon_id = dungeon_id
        m.name = name
        m.object_spawn_list = {}

        for y in range(m.height):
            for x in range(m.width):
                i = y * m.width + x
                m.grid[i] = Tile(x, y, data['grid'][i])

        m.build_edges()

        for key, o in data['objects'].iteritems():
            m.object_spawn_list[int(key)] = o

        m.player_spawn = data['player_spawn']
        m.spawn_player()
        m.spawn_objects()

        return m

    def build_edges(self):

        for t in self.grid:
            t.edges = E_NONE

        for y in range(self.height-1):
            for x in range(self.width-1):
                tile = self.get(x,y)
                up, rg = self.up(tile), self.right(tile)

                if tile.is_empty != up.is_empty:
                    tile.edges |= E_TOP
                    up.edges |= E_BOTTOM

                if tile.is_empty != rg.is_empty:
                    tile.edges |= E_RIGHT
                    rg.edges |= E_LEFT


    def export_json(self):
        jsondata = json.dumps({
            'width': self.width,
            'height': self.height,
            'grid': [t.type for t in self.grid],
            # 'edges': [t.edges for t in self.grid],
            'objects': self.object_spawn_list,
            'player_spawn': self.player_spawn
        }, separators=(',', ':'))
        return jsondata

    def save(self):
        """
        Writes a map to the server in JSON.
        """
        with open ('mapdata.json', 'w') as f:
            f.write(self.export_json())

    def despawn_object(self, o):
        # TODO remove from batch too?
        for tile in o.tiles:
            tile.objects.discard(o)
        self.objects.remove(o)
        o.sprite.delete()
        del o

    def spawn_object(self, o):
        self.objects.append(o)
        self.hash_object(o)
        if not sys.modules.has_key('gamelib.controller.headless'):
            o.sprite.batch = self._object_sprite_batch

    def spawn_player(self):

        if self.player and self.player.sprite:
            self.player.sprite.delete()

        x = self.player_spawn % self.width * MAP_TILESIZE
        y = self.player_spawn / self.width * MAP_TILESIZE
        self.player = player.Player(x, y)
        self.hash_object(self.player)

    def spawn_objects(self):

        for i, obj_type in self.object_spawn_list.iteritems():
            x = i%self.width * MAP_TILESIZE
            y = i/self.width * MAP_TILESIZE
            o = INFO[obj_type].cls(x, y)
            self.spawn_object(o)

    def despawn_objects(self):

        for tile in self.grid:
            tile.objects = set()
        self.objects = []

    # tile lookup convinience methods
    def get(self, x, y):
        return self.grid[y*self.width + x]
    def offset(self, tile, x=0, y=0):
        return self.get(tile.x+x, tile.y+y)
    def left(self, tile):
        return self.get(tile.x-1, tile.y)
    def right(self, tile):
        return self.get(tile.x+1, tile.y)
    def up(self, tile):
        return self.get(tile.x, tile.y+1)
    def down(self, tile):
        return self.get(tile.x, tile.y-1)

    def is_bound(self, tile, edge=E_ALL):
        """
        Returns true if this tile is on the edge of the map.
        May be passed an edge flag to check one or more edges specifically.
        """
        if edge & E_LEFT and tile.x == 0:
            return True
        if edge & E_BOTTOM and tile.y == 0:
            return True
        if edge & E_RIGHT and tile.x == self.width - 1:
            return True
        if edge & E_TOP and tile.y == self.height - 1:
            return True
        return False

    def in_bounds(self, tile):
        return 0 <= tile.x < self.width and 0 <= tile.y < self.height

    def change(self, x, y, type, force=False, state=None):
        """
        Modify the map and mark dirty so we rebuild the vertex list.
        """

        if x < 0 or y < 0 or x > self.width - 1 or y > self.height -1:
            return

        tile = self.get(x,y)

        # can't change boundaries
        if not force and self.is_bound(tile, E_ALL):
            return

        # cant place over objects
        existing = self.object_spawn_list.get(y*self.width+x, None)
        if existing:
            return

        if state:
            delta = TILE_INFO[type][0] # buy new tile
            delta -= TILE_INFO[tile.type][0] # sell old tile
            if state['budget'] + delta > state['wealth']:
                return False # cant afford it!
            else:
                state['budget'] += delta

        # switch the tile edges if necessary
        if type != T_EMPTY and tile.type == T_EMPTY or type == T_EMPTY and tile.type != T_EMPTY:

            # the ol swaperoo, this seems to hold true that for any given tile on the map, if we change
            # the state from empty to not empty, or vice-versa, to correctly change the edge flags, we just
            # need to simply NOT them. That is if no edges are set, set all of them. If the top-left is set,
            # set the bottom right.
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

    def place(self, x0, y0, type, state=None):
        """
        Place an object on the map.
        """

        # check tiles to make sure empty
        x1, y1 = x0 + INFO[type].cls.tile_width, y0 + INFO[type].cls.tile_height
        for y in range(y0, y1):
            for x in range(x0, x1):
                tile = self.get(x, y)
                existing = self.object_spawn_list.get(y*self.width+x, None)
                if not tile.is_empty:
                    return
                if existing:
                    return

        if type == PLAYER:
            self.player_spawn = y0*self.width+x0
            self.spawn_player()
        else:
            if state:
                if state['budget'] + INFO[type].price > state['wealth']:
                    return # can't afford it!
                else:
                    state['budget'] += INFO[type].price
            # add to spawn list
            self.object_spawn_list[y0*self.width+x0] = type

            # spawn for display on map
            self.spawn_object(INFO[type].cls(x=x0*MAP_TILESIZE, y=y0*MAP_TILESIZE))

    def unplace(self, x, y, state=None):
        """
        Remove an object from the map.
        """
        tile = self.get(x, y)
        existing = self.object_spawn_list.get(y*self.width+x, None)
        if existing:
            if state:
                state['budget'] -= INFO[existing].price
            target_obj = None
            for o in tile.objects:
                if o.pos.x / MAP_TILESIZE == x and o.pos.y / MAP_TILESIZE == y:
                    target_obj = o
            self.despawn_object(target_obj)
            del self.object_spawn_list[y*self.width+x]

    def raycast(self, origin, target):
        """
        http://www.cse.yorku.ca/~amana/research/grid.pdf
        """
        delta = target - origin
        x, y = int(origin.x)/MAP_TILESIZE, int(origin.y)/MAP_TILESIZE

        # amount to increment each cell by
        if delta.x < 0:
            step_x = -1
            factor = (origin.x % MAP_TILESIZE) / delta.x
            tmax_x = (delta*factor).magnitude
        elif delta.x > 0:
            step_x = 1
            factor = (32 - origin.x % MAP_TILESIZE) / delta.x
            tmax_x = (delta*factor).magnitude
        else:
            step_x = 0
            tmax_x = 0.0    # ray length before we cross x boundary

        if delta.y < 0:
            step_y = -1
            factor = (origin.y % MAP_TILESIZE) / delta.y
            tmax_y = (delta*factor).magnitude
        elif delta.y > 0:
            step_y = 1
            factor = (32 - origin.y % MAP_TILESIZE) / delta.y
            tmax_y = (delta*factor).magnitude
        else:
            step_y = 0
            tmax_y = 0.0    # ray length before we cross y boundary

        # ray length to travel one tile horizontally
        tdelta_x = (delta * (MAP_TILESIZE / delta.x)).magnitude
        tdelta_y = (delta * (MAP_TILESIZE / delta.y)).magnitude

        while 0 <= x < self.width and 0 <= y < self.height:

            tile = self.get(x, y)

            if not tile.is_empty:
                return tile, min(tmax_x, tmax_y)

            if tmax_x < tmax_y or step_y == 0:
                tmax_x += tdelta_x
                x += step_x
            else:
                tmax_y += tdelta_y
                y += step_y

        return None, None

    def tiles_from_object(self, obj):
        """
        Determine a range of x,y tile indices to iterate through. For objects smaller than the size of
        the grid, this will be at most 4 cells.
        """
        x0, y0 = int(obj.pos.x) / MAP_TILESIZE, int(obj.pos.y-1) / MAP_TILESIZE
        x1, y1 = int(obj.pos.x + obj.width) / MAP_TILESIZE + 1, int(obj.pos.y + obj.height) / MAP_TILESIZE + 1
        for y in range(y0, y1):
            for x in range(x0,x1):
                yield self.get(x, y)

    def hash_object(self, o):
        """
        Hash objects against the map tiles so we can quickly check what objects occupy this cell during
        collision tests.
        """

        new_tiles = set(self.tiles_from_object(o))

        # use set intersections to determine which tiles to remove the object from
        for tile in o.tiles - new_tiles:
            tile.objects.remove(o)

        # use set intersections to determine which tiles to add this object to
        for tile in new_tiles - o.tiles:
            tile.objects.add(o)

        # cache this list of tiles in the object
        # using this property is a potential alternative to calling tiles_from_object
        o.tiles = new_tiles

    def collide_objects(self, obj):
        """
        Take one object and determine any other objects it is colliding with
        """
        collisions = set()

        for tile in obj.tiles: #self.tiles_from_object(obj):
            for o in tile.objects:
                if o == obj:
                    continue
                if collide.AABB_to_AABB(o.pos, o.width, o.height, obj.pos, obj.width, obj.height):
                    collisions.add(o)
                    # resolve

        return collisions

    def collide_geometry(self, obj):
        """
        Collide one object against the map, and also resolve those collisions since we know the map doesn't move.
        """

        # assume this object is falling unless we resolve a ground collision
        on_ground = False

        # store a list of intersecting tiles to return
        collisions = []
        # if obj.pos.y in [128, 160]: print 'debuggining', obj.pos.y
        for tile in self.tiles_from_object(obj):
            # if obj.pos.y in [128, 160]: print tile.x, tile.y
            tpos = vector.Vec2d(tile.x*MAP_TILESIZE, tile.y*MAP_TILESIZE)

            # do nothing for empty tiles
            if tile.type == T_EMPTY:
                continue

            # check for a broad AABB intersection
            elif collide.AABB_to_AABB(tpos, MAP_TILESIZE, MAP_TILESIZE, obj.pos, obj.width, obj.height):

                # check for individual edge intersections (only if this tile has that edge flag set)
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

                # add this tile to collisions list since we performed a projection out of it
                if projected_edge[1] != 0x0:
                    collisions.append(tile)

                # calculate resolution, if we project out the top, inform the object it's now on the ground
                if projected_edge[1] == E_TOP:
                    obj.pos.y += projected_edge[0]
                    # obj.pos0.y = obj.pos.y
                    on_ground = True
                elif projected_edge[1] == E_RIGHT:
                    obj.pos.x += projected_edge[0]
                elif projected_edge[1] == E_BOTTOM:
                    obj.pos.y -= projected_edge[0]
                elif projected_edge[1] == E_LEFT:
                    obj.pos.x -= projected_edge[0]

        # all done
        if on_ground:
            obj.ground()
        else:
            obj.fall()

        return collisions


    def draw(self):
        """
        Render the current map, checking if the vertex list has been dirtied and needs to be rebuilt.
        """
        # check if we need to rebuild the vertex list. We defer this until drawing time so that
        # every operation that modifies the map doesn't need to rebuild this list every time.
        if self._vertex_list_dirty:
            self.rebuild_vertices()
            self._vertex_list_dirty = False

        # draw the objects batch
        self._object_sprite_batch.draw()

        # draw the effects batch
        fx._fx_sprite_batch.draw()

        # bind the tile texture and draw the whole map
        glEnable(GL_TEXTURE_2D)
        glBindTexture(self.tiles_tex.target, self.tiles_tex.id)
        self._vertex_list.draw(GL_QUADS)

        # draw the highlight square
        if self._highlight.enabled:
            glDisable(GL_TEXTURE_2D)
            glColor4f(1,1,1,.5)
            self._highlight.draw(GL_QUADS)
            glColor4f(1,1,1,1)
            glEnable(GL_TEXTURE_2D)


    def rebuild_vertices(self):
        """
        Cycle through our map data and build a grid of quads with correct texcoords. This will be used
        to render the map.
        """
        self._vertex_list.delete()
        vertices = []
        tex_coords = []

        for tile in self.grid:

            # don't bother creating vertices for empty tiles
            if tile.type == T_EMPTY:
                continue

            # add vertices and tex coords for this tile
            vertices += tile.quad

            if tile.type not in [T_BLOCK_WOOD, T_BLOCK_CONCRETE, T_BLOCK_STEEL]:
                tex_coords += tile.tex(tile.type, R_0)
                continue

            n_up = self.up(tile) if not self.is_bound(tile, E_TOP) else None
            n_rg = self.right(tile) if not self.is_bound(tile, E_RIGHT) else None
            n_dn = self.down(tile) if not self.is_bound(tile, E_BOTTOM) else None
            n_lf = self.left(tile) if not self.is_bound(tile, E_LEFT) else None

            edges = tile.edges

            if n_up and n_up.type != tile.type:
                edges |= E_TOP
            if n_rg and n_rg.type != tile.type:
                edges |= E_RIGHT
            if n_dn and n_dn.type != tile.type:
                edges |= E_BOTTOM
            if n_lf and n_lf.type != tile.type:
                edges |= E_LEFT

            tex_coords += tile.tex(tile.type + TEX_MUT[edges][0], TEX_MUT[edges][1])

            # add corner decals on stacked tiles
            if n_up and n_lf and n_up.type == tile.type and n_lf.type == tile.type and self.offset(tile, -1, 1).type != tile.type:
                vertices += tile.quad
                tex_coords += tile.tex(tile.type + 96, R_0)

            if n_up and n_rg and n_up.type == tile.type and n_rg.type == tile.type and self.offset(tile, 1, 1).type != tile.type:
                vertices += tile.quad
                tex_coords += tile.tex(tile.type + 96, R_90)

            if n_dn and n_rg and n_dn.type == tile.type and n_rg.type == tile.type and self.offset(tile, 1, -1).type != tile.type:
                vertices += tile.quad
                tex_coords += tile.tex(tile.type + 96, R_180)

            if n_dn and n_lf and n_dn.type == tile.type and n_lf.type == tile.type and self.offset(tile, -1, -1).type != tile.type:
                vertices += tile.quad
                tex_coords += tile.tex(tile.type + 96, R_270)

        self._vertex_list = pyglet.graphics.vertex_list(len(vertices)/2, 'v2f', 't2f')
        self._vertex_list.vertices = vertices
        self._vertex_list.tex_coords = tex_coords

    def highlight(self, x, y):
        """
        Highlight a given tile location.
        """

        if x < 0 or y < 0 or x > self.width - 1 or y > self.height -1:
            self._highlight.enabled = False
            return

        tile = self.get(x, y)
        # print tile.x, tile.y, tile.edges
        # can't highlight boundaries
        if self.is_bound(tile):
            self._highlight.enabled = False
        else:
            self._highlight.vertices = tile.quad
            self._highlight.enabled = True

class Tile(object):
    """
    A Tile is any given square of the map.
    """
    def __init__(self, x, y, type, edges=0):
        self.x = x
        self.y = y
        self.type = type
        self.edges = edges

        # set of references to objects contained here
        self.objects = set()

    def tex(self, index, rot=0, flip=0):
        tx0 = float(index % 16) / 16.0
        ty0 = float(index / 16) / 16.0
        tx1 = tx0 + 1.0 / 16.0
        ty1 = ty0 + 1.0 / 16.0
        tex_coords = [tx0, ty0, tx0, ty1, tx1, ty1, tx1, ty0]
        return tex_coords[rot*2:] + tex_coords[:rot*2]

    @property
    def is_empty(self):
       return self.type == T_EMPTY

    def has_edge(self, edge):
        return self.edges & edge

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
