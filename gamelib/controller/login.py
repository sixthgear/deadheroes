from pyglet.text import document, layout, caret
from pyglet.gl import *
from pyglet.window import key
from pyglet import clock
from gamelib import collide
from gamelib.ui.widgets import TextWidget
from gamelib.util_hax import defer

STATUS = {
    "login" : "Status: Please Login",
    "invalid": "Status: Password Incorrect",
    "badsession": "Status: Bad Session, Please Login",
    "down": "Status: Unable to reach server"
}

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

        pyglet.text.Label(
            'THE HEROES ARE ', 
            x=640, y=500, 
            font_size=36, font_name='DYLOVASTUFF', anchor_x='center', anchor_y='bottom',
            color=(100, 100, 100, 255), batch = self.batch)

        pyglet.text.Label(
            'DEAD', 
            x=640, y=520, 
            font_size=120, font_name='DYLOVASTUFF', anchor_x='center', anchor_y='top',
            color=(150, 100, 100, 255), batch=self.batch)

        self.status =  pyglet.text.Label(STATUS['login'], x = 550, y = 220, font_name='DYLOVASTUFF',
            color=(0, 0, 0, 255), batch = self.batch)

        pyglet.text.Label('NAME', x = 454, y = 303, font_name='DYLOVASTUFF',
            color=(0, 0, 0, 255), batch = self.batch)
        pyglet.text.Label('PASSWORD', x = 454, y = 263, font_name='DYLOVASTUFF',
            color=(0, 0, 0, 255), batch = self.batch)

        self.widgets = {
            'user': TextWidget('', 550, 300, 260, self.batch),
            'password': TextWidget('', 550, 260, 260, self.batch)
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
                user = self.widgets['user'].get_text()
                password = self.widgets['password'].get_text()

                defer(self.window.on_login, user, password)
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

    def on_login_failure(self):
        self.status.text = STATUS['invalid']

    def on_no_connection(self):
        self.status.text = STATUS['down']

    def cleanup(self):
        pass
