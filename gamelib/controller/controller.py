from pyglet.gl import *
from pyglet.window import key

import edit
import play

class Controller(pyglet.window.Window):

    properties = {
        'width': 1280, 
        'height': 800, 
        'caption': 'Pyweek 16',
        'fullscreen': False
    }

    def __init__(self):
        super(Controller, self).__init__(**self.properties)
        self.set_vsync(True)
        self.state = None
        self.fps_display = pyglet.clock.ClockDisplay()
                
    def switch(self, state):
        if self.state:
            self.remove_handlers(self.state)
            self.remove_handlers(self.state.keys)
        self.state = state(self)
        self.push_handlers(self.state)
        self.push_handlers(self.state.keys)
        
    def title(self):        
        self.switch(title.Title)

    def play(self):        
        self.switch(edit.Game)

    def on_key_press(self, symbol, modifiers):        
        if (modifiers & (key.MOD_CTRL | key.MOD_COMMAND)) and symbol == key.Q:
            pyglet.app.exit()
        elif (modifiers & (key.MOD_CTRL | key.MOD_COMMAND)) and symbol == key.F:
            self.set_fullscreen(not self.fullscreen)
            if not self.fullscreen:
                self.width = self.properties['width']
                self.height = self.properties['height']

    def on_resize(self, width, height):        
        # Based on the default with more useful clipping planes
        gl.glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1.0, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)        
        
    def setup_gl(self):
        """
        Configure the OpenGL context.
        """        
        pass

    def run(self):
        """
        Setup the environment and run with it.
        """            
        self.setup_gl()
        self.play()
        pyglet.app.run()
        
            
            
        