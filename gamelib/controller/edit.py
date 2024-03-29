# from objects import player
import random
from gamelib import vector
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib.objects.info import *
from gamelib.objects import obj
from gamelib import map
from gamelib.ui import hud_edit
from gamelib.util_hax import defer

MODE_TILE =     0x00
MODE_OBJ =      0x01
MODE_CHUNK =    0x02

class Editor(object):
    """
    The Dungeon Editor
    """    

    def __init__(self, window, dungeon=None):
        self.window = window
        self.music = None                
        self.keys = key.KeyStateHandler()
        self.cursor = [0,0]
        self.hud = hud_edit.HUD()

        if dungeon:
            self.map = dungeon
        else:
            self.map = map.Map(40, 23)
        
        self.mode = MODE_TILE
        self.selected_tile = map.T_BLOCK_WOOD
        self.selected_object = ZOMBIE
        self.ghost_cursor = pyglet.sprite.Sprite(pyglet.image.create(0,0))
        self.ghost_cursor.opacity = 128

        self.state = {
            'budget': self.map.pending_budget, # self.window.player_data['wealth'] # TODO LOAD THIS FORM SERVER
            'wealth': self.window.player_data['wealth']
        }
        self.hud.alter_budget(self.state['budget'], self.state['wealth'])
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.9,0.9,0.9,1.0)

    def update(self, dt):
        pass
    
    def on_draw(self):
        self.window.clear()

        if self.mode == MODE_CHUNK:
            pass
        else:
            self.map.draw()

        self.hud.draw()
        self.ghost_cursor.draw()

        if self.window.show_fps: 
            self.window.fps_display.draw()

    def save(self):
        json = self.map.export_json()        
        return self.window.session.upload_dungeon(json)

    def on_key_press(self, symbol, modifiers):

        if symbol == key.ESCAPE:
            self.map.save()
            self.save()
            defer(self.window.menu)

        if symbol == key.S:
            self.save()            
            # defer(self.window.menu)

        if symbol == key.TAB:
            self.map.save()
            dungeon_id = self.save()
            if dungeon_id:
                # self.window.refresh_player_data()
                self.map.dungeon_id = dungeon_id
                self.map.name = self.window.player_data['name']
                self.map.pending_budget = self.state['budget']
                defer(self.window.play, self.map)
            else:
                print 'Error: the map couldn\'t be saved!'


        if symbol == key.GRAVE:
            # enter chunk editing mode

            self.mode = ((self.mode + 1) % 3)

            if self.mode == MODE_TILE:
                self.hud.labels['title'].text = 'DESIGN YOUR DUNGEON (TILE)'
            elif self.mode == MODE_OBJ:
                self.hud.labels['title'].text = 'DESIGN YOUR DUNGEON (OBJ)'
            elif self.mode == MODE_CHUNK:
                self.hud.labels['title'].text = 'DESIGN YOUR DUNGEON (CHNK)'

        if symbol == key.G:
            # generate level from chunks
            pass

        # clear map
        if symbol == key.C:
            self.map = map.Map(40, 23)
        
        if symbol == key.M:
            for o in self.map.objects:
                print o

        if self.mode in [MODE_TILE, MODE_CHUNK]:
            return self.on_key_press_tile(symbol, modifiers)
        if self.mode == MODE_OBJ:
            return self.on_key_press_obj(symbol, modifiers)
        if self.mode == MODE_CHUNK:
            return self.on_key_press_chunk(symbol, modifiers)



    def on_key_press_tile(self, symbol, modifiers):

        # set block type
        if symbol == key._0:
            self.mode = MODE_TILE
            self.selected_tile = map.T_EMPTY
        if symbol == key._1:
            self.mode = MODE_TILE
            self.selected_tile = map.T_BLOCK_WOOD
        if symbol == key._2:
            self.mode = MODE_TILE
            self.selected_tile = map.T_BLOCK_CONCRETE
        if symbol == key._3:
            self.mode = MODE_TILE
            self.selected_tile = map.T_BLOCK_STEEL
        if symbol == key._4:
            self.mode = MODE_TILE
            self.selected_tile = map.T_SPIKES
        if symbol == key._5:
            self.mode = MODE_TILE
            self.selected_tile = map.T_LAVA            

        x = (self.selected_tile%16) * map.MAP_TILESIZE
        y = (self.selected_tile/16) * map.MAP_TILESIZE
        self.ghost_cursor.image = map.Map.tiles_tex.get_region(x,y,32,32)

    def on_key_press_obj(self, symbol, modifiers):

        if symbol == key._0:
            self.mode = MODE_OBJ
            self.selected_object = PLAYER
        if symbol == key._1:
            self.mode = MODE_OBJ
            self.selected_object = ZOMBIE
        if symbol == key._2:
            self.mode = MODE_OBJ
            self.selected_object = ROBOT
        if symbol == key._3:
            self.mode = MODE_OBJ
            self.selected_object = LAUNCHER
        if symbol == key._4:
            self.mode = MODE_OBJ
            self.selected_object = EMITTER
        if symbol == key._5:
            self.mode = MODE_OBJ
            self.selected_object = DOOR
        if symbol == key._6:
            self.mode = MODE_OBJ
            self.selected_object = CHEST
        if symbol == key._7:
            self.mode = MODE_OBJ
            self.selected_object = ANVIL            

        t = pyglet.resource.texture('sprites.png')
        index = INFO[self.selected_object].cls.tex_index
        width = INFO[self.selected_object].cls.tile_width * map.MAP_TILESIZE
        height = INFO[self.selected_object].cls.tile_height * map.MAP_TILESIZE
        x = (index%16) * map.MAP_TILESIZE
        y = (index/8) * map.MAP_TILESIZE
        self.ghost_cursor.image = t.get_region(x,y,width,height)

    def on_key_press_chunk(self, symbol, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy): 
        x = max(0, min(self.window.width-1, x))
        y = max(0, min(self.window.height-1, y))
        tx, ty = (x / map.MAP_TILESIZE, y / map.MAP_TILESIZE)
        self.cursor = [tx, ty]
        self.map.highlight(*self.cursor)
        self.ghost_cursor.x = self.cursor[0] * map.MAP_TILESIZE
        self.ghost_cursor.y = self.cursor[1] * map.MAP_TILESIZE
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x = max(0, min(self.window.width-1, x))
        y = max(0, min(self.window.height-1, y))
        if x / map.MAP_TILESIZE != self.cursor[0] or y / map.MAP_TILESIZE != self.cursor[1]:
            self.on_mouse_press(x, y, buttons, modifiers)
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        x = max(0, min(self.window.width-1, x))
        y = max(0, min(self.window.height-1, y))        

        if modifiers & (key.MOD_CTRL | key.MOD_COMMAND):
            v1 = vector.Vec2d(16,16)
            v2 = vector.Vec2d(x,y)
            
            self.hud._label_batch.add(2, GL_LINES, None, ('v2f', [v1.x, v1.y, v2.x, v2.y]), ('c4f', [1,1,1,1,1,1,1,1]))
            for t in self.map.raycast(v1,v2):
                self.map.change(t.x, t.y, map.T_BLOCK_CONCRETE)                
            return

        if self.mode == MODE_TILE and button == 1:
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_tile, state=self.state)
        elif self.mode == MODE_OBJ and button == 1:
            self.map.place(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_object, state=self.state)
        elif self.mode == MODE_TILE and button == 4:
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, 0, state=self.state)
        elif self.mode == MODE_OBJ and button == 4:            
            self.map.unplace(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, state=self.state)

        self.hud.alter_budget(self.state['budget'], self.state['wealth'])
                        
    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def cleanup(self):
        self.map._highlight.enabled = False