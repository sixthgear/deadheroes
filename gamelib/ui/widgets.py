import pyglet
from pyglet import text
from pyglet import graphics
from gamelib.util_hax import defer, prettydate


class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', [200, 200, 220, 255] * 4)
        )

class Widget(object):

        def hit_test(self, x, y):
            return (0 < x - self.layout.x < self.layout.width and 0 < y - self.layout.y < self.layout.height)

class TextWidget(Widget):
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
            dict(color=(0, 0, 0, 255))
        )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, batch)
        self.lose_focus()

    def lose_focus(self):
    	self.caret.visible = False
    	self.caret.mark = 0
    	self.caret.position = 0

    def focus(self):
    	self.caret.visible = True
        self.caret.mark = 0
        self.caret.position = len(self.document.text)

    def on_mouse_press(self, x, y, button, modifiers):
    	self.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    	self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
    	self.caret.on_text(text)

    def on_text_motion(self, motion):
    	self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)

    def get_text(self):
    	return self.document.text

class DungeonListingWidget(Widget):

    def __init__(self, x, y, id, username, age, value, attempts, batch):

        # self.id = id
        # self.age = age
        # self.attempts = attempts

        self.id = id
        self.x = x
        self.y = y

        self.labels = {
        'title': text.Label(
            '%s' % username, 
            x=x, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=(100,100,100,255),
            batch=batch), 

        'age': text.Label(
            '%s' % prettydate(int(age)),
            x=x+400, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=(100,100,100,255),
            batch=batch), 

        'value': text.Label(
            '$%d' % value,
            x=x+300, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=(100,100,100,255),
            batch=batch), 

        'attempts': text.Label(
            '%d' % attempts, 
            x=x+600, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=(100,100,100,255),
            batch=batch), 
        }
