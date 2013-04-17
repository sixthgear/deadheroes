# from objects import player
import random
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import vector
from gamelib import map
from gamelib.ui import hud_edit


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
        except:
            self.map = map.Map(40, 23)

        self.mode = map.T_BLOCK_WOOD
        self.init_gl()

    def init_gl(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.1,0.05,0.0,1.0)

    def update(self, dt):
        pass
    
    def on_draw(self):
        self.window.clear()
        self.map.draw()
        self.hud.draw()
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
            self.mode = map.T_EMPTY
        if symbol == key._1:
            self.mode = map.T_BLOCK_WOOD
        if symbol == key._2:
            self.mode = map.T_BLOCK_CONCRETE
        if symbol == key._3:
            self.mode = map.T_BLOCK_STEEL

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
        if button == 1: 
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, self.mode)         
        else:          
            self.map.change(x / map.MAP_TILESIZE, y / map.MAP_TILESIZE, 0)
                        
    def on_mouse_release(self, x, y, button, modifiers):
        pass
