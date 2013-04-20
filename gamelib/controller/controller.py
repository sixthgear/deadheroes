from pyglet.gl import *
from pyglet import clock
from pyglet.window import key
from gamelib import map
from gamelib import fixedsteploop
from gamelib.network import Session
from gamelib.objects import fx
from gamelib.controller import login, menu, edit, play, replay

pyglet.resource.add_font('DYLOVASTUFF.ttf')
pyglet.font.load('DYLOVASTUFF')

class Controller(pyglet.window.Window):

    DT = 1 / 60.0
    DT2 = DT * DT

    properties = {
        'width': 1280, 
        'height': 800, 
        'caption': 'The Heroes Are Dead',
        'fullscreen': False
    }

    def __init__(self):
        super(Controller, self).__init__(**self.properties)
        self.set_vsync(False)
        self.states = {}
        self.current_state = None
        self.fps_display = pyglet.clock.ClockDisplay()
        self.show_fps = True
        self.timer = fixedsteploop.FixedStepLoop(self.update, self.DT, self.DT*2)
        self.session = Session(self)
        self.player_data = {}


    def refresh_player_data(self):
        self.player_data = self.session.get_player()

    def switch(self, name, persist=False, state=None):
        """
        This function will switch contexts between different input/rending controllers.
        """
        
        self.refresh_player_data()

        if self.current_state:
            self.remove_handlers(self.current_state)
            self.remove_handlers(self.current_state.keys)
            self.current_state.cleanup()

        if persist:
            if self.states.has_key(name):
                state = self.states[name]
            else:
                self.states[name] = state
        
        self.current_state = state

        self.push_handlers(self.current_state)
        self.push_handlers(self.current_state.keys)        


    def login(self, dt=0.0):
        login_screen = login.Login(window=self)
        self.switch('login', persist=False, state=login_screen)

    def on_login(self, user, password):        
        self.session.login(user, password)        
        self.menu()

    def on_no_connection(self):
        pass

    def on_logged_in(self, response):
        #self.edit(dt = 0.0)
        print response

    def on_login_failure(self, response):
        if self.states.has_key('login'):
            self.states['login'].on_login_failure()

    def menu(self):        
        self.switch('menu', persist=False, state=menu.Menu(window=self))

    def edit(self, dungeon=None):
        # print 'switching to edit'
        # if self.states.has_key('edit'):
        #     self.states['edit'].map.init_state()
        #     self.switch('edit', persist=True)
        # else:                    
        self.switch('edit', persist=False, state=edit.Editor(window=self, dungeon=dungeon))


    def load(self, dungeon_id, name):
        data = self.session.get_dungeon(dungeon_id)        
        return map.Map.load(dungeon_id, name, data)

    def play(self, dungeon):
        self.switch('play', persist=False, state=play.Game(window=self, dungeon=dungeon))
        
    def replay(self, map, rep):
        """
        """        
        state = replay.Replay(window=self, dungeon=map, replay=rep)
        state.save()
        
        self.switch('replay', state)

    def update(self, dt):
        self.current_state.update(self.DT2)

    def on_key_press(self, symbol, modifiers):        

        if (modifiers & (key.MOD_CTRL | key.MOD_COMMAND)) and symbol == key.Q:
            pyglet.app.exit()

        elif (modifiers & (key.MOD_CTRL | key.MOD_COMMAND)) and modifiers & key.MOD_ALT and symbol == key.F:
            self.show_fps = not self.show_fps            

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
        self.login()
        # self.edit()
        pyglet.app.run()
