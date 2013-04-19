import pyglet
from pyglet import text
from pyglet import graphics
from pyglet.window import key
from gamelib.util_hax import defer
from gamelib.ui.widgets import DungeonListingWidget
from gamelib import collide
from gamelib.objects.obj import Point

class Menu(object):

    per_page = 10

    def __init__(self, window):
        self.window = window
        self.music = None
        self.keys = key.KeyStateHandler()
        self._label_batch = graphics.Batch()

        self.labels = {
        'money': text.Label(
            '1,000,000 EVIL DOLLARS', 
            x=160, y=768, 
            font_size=12, font_name="Arial", anchor_x='left', anchor_y='center', 
            color=(100,100,100,255),
            batch=self._label_batch),  

        'title': text.Label(
            'RAID A DUNGEON', 
            x=640, y=768, 
            font_size=24, font_name="Arial", anchor_x='center', anchor_y='center',
            color=(100,100,100,255),
            batch=self._label_batch),        
        }

        self.page_start = 0

        self.dungeons = self.window.session.dungeons()
        self.dungeons_widgets = []

        for i in range(self.page_start, min(len(self.dungeons), self.page_start+self.per_page)):
        
            d = DungeonListingWidget(
                x=64,
                y=600 - (i - self.page_start) * 24,
                id=self.dungeons[i]['id'], 
                age=self.dungeons[i]['age'], 
                attempts=self.dungeons[i]['attempts'], 
                batch=self._label_batch
            )                
            self.dungeons_widgets.append(d)
            self.window.push_handlers(d)
            
        print self.dungeons

    def update(self, dt):
        pass

    def on_draw(self):
        self.window.clear()
        self._label_batch.draw()
        self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            defer(self.window.edit)

        if symbol == key.TAB:
            pass

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_press(self, x, y, button, modifiers):
        
        for d in self.dungeons_widgets:
            if collide.AABB_to_AABB(Point(x,y), 0, 0, Point(d.x, d.y), 800, 24):
                # defer(self.window.play)
                m = self.window.load(d.id)
                defer(self.window.play, m)
                # print dungeon

    def cleanup(self):
        for d in self.dungeons:
            self.window.remove_handlers(d)