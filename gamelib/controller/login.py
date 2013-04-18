from pyglet.text import document, layout, caret
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import collide
from gamelib.ui.widgets import TextWidget

class Login(object):
    """
    The Login Screen
    """

    def __init__(self, window):
        self.window = window
        self.music = None
        self.keys = key.KeyStateHandler()
        self.batch = pyglet.graphics.Batch()
        self.focused = None

        pyglet.text.Label('Name:', x = 10, y = 100,
            color=(0, 0, 0, 255), batch = self.batch),
        pyglet.text.Label('Password:', x = 10, y = 60,
            color=(0, 0, 0, 255), batch = self.batch)

        self.widgets = {
            'user': TextWidget('', 200, 100, self.window.width - 210, self.batch),
            'password': TextWidget('', 200, 60, self.window.width - 210, self.batch)
        }

        self.set_focus(self.widgets['user'])

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

    def on_text(self, text):
        if text == '\r':
            return

        if self.focused:
            self.focused.on_text(text)

    def on_text_motion(self, motion):
        if self.focused:
            self.focused.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.focused:
            self.focused.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            if self.focused == self.widgets['user']:
                self.set_focus(self.widgets['password'])
            else:
                print self.widgets['user'].get_text()
                print self.widgets['password'].get_text()
            return

        if symbol == key.TAB:
            if self.focused == self.widgets['user']:
                self.set_focus(self.widgets['password'])
            else:
                self.set_focus(self.widgets['user'])
            return

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        for widget in self.widgets.values():
            if widget.hit_test(x, y):
                cursor = self.window.get_system_mouse_cursor('text')
                self.window.set_mouse_cursor(cursor)
                return
        else:
            self.window.set_mouse_cursor(None)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.focused:
            self.focused.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        for widget in self.widgets.values():
            if widget.hit_test(x, y):
                self.set_focus(widget)
                widget.on_mouse_press(x, y, button, modifiers)
                return
        else:
            self.set_focus(None)

    def set_focus(self, widget):
        if self.focused:
            self.focused.lose_focus()

        self.focused = widget

        if not self.focused:
            return

        self.focused.focus()
