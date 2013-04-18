from pyglet.gl import *
from pyglet import clock
from pyglet.window import key
from gamelib import fixedsteploop

import copy
import edit
import play
import replay
import login

class Controller(pyglet.window.Window):

    DT = 1 / 60.0
    DT2 = DT * DT

    properties = {
        'width': 1280, 
        'height': 800, 
        'caption': 'Pyweek 16',
        'fullscreen': False
    }

    def __init__(self):
        super(Controller, self).__init__(**self.properties)
        self.set_vsync(False)        
        self.states = {}
        self.current_state = None
        self.fps_display = pyglet.clock.ClockDisplay()        
        self.timer = fixedsteploop.FixedStepLoop(self.update, self.DT, self.DT*2)
                
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
        


    def login(self, dt=0.0):
        self.switch('login', login.Login(window=self))


    def edit(self, dt=0.0):
        if self.states.has_key('edit'):
            self.states['edit'].map.init_state()
            
        self.switch('edit', edit.Editor(window=self))


    def play(self, dt=0.0):

        if self.states.has_key('play'):
            del self.states['play']

        d = self.states['edit'].map

        self.switch('play', play.Game(window=self, dungeon=d))
        

    def replay(self, dt=0.0):

        if self.states.has_key('replay'):
            del self.states['replay']

        r = self.states['play'].replay
        d = self.states['play'].map
        state = replay.Replay(window=self, dungeon=d, replay=r)
        state.save()
        
        self.switch('replay', state)

    def update(self, dt):
        self.current_state.update(self.DT2)

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
        # self.login()
        self.edit()
        pyglet.app.run()
