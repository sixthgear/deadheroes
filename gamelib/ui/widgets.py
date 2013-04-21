import pyglet
from pyglet import text
from pyglet import graphics
from gamelib.util_hax import defer


class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, batch=None, color=(200, 200, 220, 255)):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', color * 4)
        )

class Widget(object):

        def __init__(self, label, x, y, width, height, batch):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

        def hit_test(self, x, y):
            return (0 < x - self.x < self.width and 0 < y - self.y < self.height)

class Button(Widget):

    def __init__(self, label, x, y, width, height, batch, callback):

        super(Button, self).__init__(label, x, y, width, height, batch)

        self.callback = callback
        pad = 4
        self.rect = Rectangle(
            x - pad, y - pad, 
            x + width + pad, y + height + pad, 
            batch=batch, color=(200,200,200,255)
        )
        self.label = text.Label(
            label, 
            x=x+width/2, y=y+height/2, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='center', anchor_y='center', 
            color=(0,0,0,255),
            batch=batch)

    def on_mouse_press(self, x, y, button, modifiers):        
        if self.hit_test(x,y):
            defer(self.callback)
            return True
        else:
            return False

class TextWidget(Widget):

    def __init__(self, label, x, y, width, batch):

        self.document = pyglet.text.document.UnformattedDocument(label)
        self.document.set_style(0, len(self.document.text),
            dict(color=(0, 0, 0, 255), font_name='DYLOVASTUFF')
        )
        font = self.document.get_font()
        height = font.ascent - font.descent

        super(TextWidget, self).__init__(label, x, y, width, height, batch)

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 4
        self.rect = Rectangle(x - pad, y - pad,
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

    def on_text(self, label):
    	self.caret.on_text(label)

    def on_text_motion(self, motion):
    	self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        self.caret.on_text_motion_select(motion)

    def get_text(self):
    	return self.document.text

class DungeonListingWidget(Widget):

    def __init__(self, x, y, id, username, age, value, attempts, batch, color=(100,100,100,255)):

        # self.id = id
        # self.age = age
        # self.attempts = attempts

        self.id = id
        self.username = username
        self.x = x
        self.y = y

        self.labels = {
        'title': text.Label(
            '%s' % username, 
            x=x, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=color,
            batch=batch), 

        'value': text.Label(
            '%s' % value,
            x=x+400, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='right', anchor_y='bottom', 
            color=color,
            batch=batch), 

        'age': text.Label(
            '%s' % age,
            x=x+430, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='left', anchor_y='bottom', 
            color=color,
            batch=batch), 
    
        'attempts': text.Label(
            '%s' % attempts, 
            x=x+650, y=y, 
            font_size=16, font_name="DYLOVASTUFF", anchor_x='right', anchor_y='bottom', 
            color=color,
            batch=batch), 
        }
