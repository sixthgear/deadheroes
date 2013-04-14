from pyglet.gl import *
from pyglet import clock
from pyglet.window import key

import edit
import play

class Controller(pyglet.window.Window):

    DT = 1.0 / 60

    properties = {
        'width': 1280, 
        'height': 800, 
        'caption': 'Pyweek 16',
        'fullscreen': False
    }

    def __init__(self):
        super(Controller, self).__init__(**self.properties)
        self.set_vsync(True)
        self.states = {}
        self.current_state = None
        self.fps_display = pyglet.clock.ClockDisplay()
        self.timer = clock.schedule_interval(self.update, self.DT)
                
    def switch(self, name, state=None):

        if self.current_state:
            self.remove_handlers(self.current_state)
            self.remove_handlers(self.current_state.keys)

        if self.states.has_key(name):
            state = self.states[name]
        else:
            self.states[name] = state
        
        self.current_state = state
        self.push_handlers(self.current_state)
        self.push_handlers(self.current_state.keys)
        
    def edit(self, dt=0.0):
        self.switch('edit', edit.Game(window=self))

    def play(self, dt=0.0):
        if self.states.has_key('edit'):
            self.switch('play', play.Game(window=self, dungeon=self.states['edit'].map))
        else:
            self.switch('play', play.Game(window=self))

    def update(self, dt):
        self.current_state.update(self.DT)

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
        self.edit()
        pyglet.app.run()
