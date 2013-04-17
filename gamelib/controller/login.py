from pyglet.text import document, layout, caret
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import collide

# class FormFieldGroup()

class Login(object):
    """
    The Login Screen
    """

    def __init__(self, window):     
        self.window = window
        self.music = None                
        self.keys = key.KeyStateHandler()
        
        self.batch = pyglet.graphics.Batch()

        self.username = layout.IncrementalTextLayout(document.UnformattedDocument(), 200, 32, batch=self.batch)
        self.username.x, self.username.y = 200, 200
        # self.username.background_color = (255,255,255,255)
        self.caret = caret.Caret(self.username, batch=self.batch)
        self.window.push_handlers(self.caret)

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
        self.batch.draw()
        # self.caret.draw()
        self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):

        if symbol == key.ESCAPE:            
            pyglet.app.exit()

        if symbol == key.TAB:
            pass

        if symbol == key.ENTER:
            pass



    def on_mouse_motion(self, x, y, dx, dy): 
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass
                        
    def on_mouse_release(self, x, y, button, modifiers):
        pass    