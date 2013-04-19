# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib.objects.info import *
from gamelib import map
from gamelib.ui import hud_edit

MODE_TILE = 0x01
MODE_OBJ = 0x02

class Editor(object):
    """
    The Dungeon Editor
    """    

    def __init__(self, window):     
        self.window = window
        self.music = None                
        self.keys = key.KeyStateHandler()
        self.cursor = [0,0]
        self.hud = hud_edit.HUD()

        try:
            self.map = map.Map.load(0)
        except IOError:
            self.map = map.Map(40, 23)
        
        self.mode = MODE_TILE
        self.selected_tile = map.T_BLOCK_WOOD
        self.selected_object = ZOMBIE

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
        if self.window.show_fps: 
            self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):

        if symbol == key.ESCAPE:
            self.map.save()
            pyglet.app.exit()

        if symbol == key.TAB:
            pyglet.clock.schedule_once(self.window.play, 0.0)
            self.map._highlight.enabled = False

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



    def on_mouse_motion(self, x, y, dx, dy): 
        x = max(0, min(self.window.width-1, x))
        y = max(0, min(self.window.height-1, y))
        self.cursor = [x / map.MAP_TILESIZE, y / map.MAP_TILESIZE]
        self.map.highlight(*self.cursor)

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
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_tile)
        elif self.mode == MODE_OBJ and button == 1:
            self.map.place(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.selected_object)
        elif self.mode == MODE_TILE and button == 4:
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, 0)
        elif self.mode == MODE_OBJ and button == 4:            
            self.map.unplace(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE)

                        
    def on_mouse_release(self, x, y, button, modifiers):
        pass
