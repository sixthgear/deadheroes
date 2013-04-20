# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib.objects.info import *
from gamelib.objects import obj
from gamelib import map
from gamelib.ui import hud_edit
from gamelib.util_hax import defer

MODE_TILE = 0x01
MODE_OBJ = 0x02

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
            'budget': self.window.player_data['wealth'] # TODO LOAD THIS FORM SERVER
        }
        self.hud.alter_budget(self.state['budget'])
        
                
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
            if self.save():
                self.window.refresh_player_data()
                defer(self.window.play, self.map)
            else:
                print 'Error: the map couldn\'t be saved!'


        # clear map
        if symbol == key.C:
            self.map = map.Map(40, 23)

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

        if symbol == key.Q:
            self.mode = MODE_OBJ
            self.selected_object = PLAYER
        if symbol == key.W:
            self.mode = MODE_OBJ
            self.selected_object = ZOMBIE
        if symbol == key.E:
            self.mode = MODE_OBJ
            self.selected_object = ROBOT
        if symbol == key.R:
            self.mode = MODE_OBJ
            self.selected_object = LAUNCHER
        if symbol == key.T:
            self.mode = MODE_OBJ
            self.selected_object = DOOR
        if symbol == key.Y:
            self.mode = MODE_OBJ
            self.selected_object = CHEST
        if symbol == key.U:
            self.mode = MODE_OBJ
            self.selected_object = ANVIL

        if self.mode == MODE_OBJ:
            t = pyglet.resource.texture('sprites.png')

            index = INFO[self.selected_object].cls.tex_index
            width = INFO[self.selected_object].cls.tile_width * map.MAP_TILESIZE
            height = INFO[self.selected_object].cls.tile_height * map.MAP_TILESIZE
            x = (index%16) * map.MAP_TILESIZE
            y = (index/8) * map.MAP_TILESIZE

            self.ghost_cursor.image = t.get_region(x,y,width,height)
                        
        else:
            x = (self.selected_tile%16) * map.MAP_TILESIZE
            y = (self.selected_tile/16) * map.MAP_TILESIZE
            self.ghost_cursor.image = map.Map.tiles_tex.get_region(x,y,32,32)


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
        if self.mode == MODE_TILE and button == 1:
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_tile, state=self.state)
        elif self.mode == MODE_OBJ and button == 1:
            self.map.place(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_object, state=self.state)
        elif self.mode == MODE_TILE and button == 4:
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, 0, state=self.state)
        elif self.mode == MODE_OBJ and button == 4:            
            self.map.unplace(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, state=self.state)

        self.hud.alter_budget(self.state['budget'])
                        
    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def cleanup(self):
        self.map._highlight.enabled = False