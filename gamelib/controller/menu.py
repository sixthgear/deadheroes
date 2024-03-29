import pyglet
from pyglet import text
from pyglet import graphics
from pyglet.window import key
from gamelib.util_hax import defer, prettydate
from gamelib.ui.widgets import DungeonListingWidget
from gamelib import collide
from gamelib.objects.obj import Point

class Menu(object):

    per_page = 12

    def __init__(self, window):
        self.window = window
        self.music = None
        self.keys = key.KeyStateHandler()
        self._label_batch = graphics.Batch()
        self.player_dungeon_widget = None
        self.labels = {

        'heroes': text.Label(
            'THE HEROES ARE', 
            x=454, y=730, 
            font_size=36, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='bottom',
            color=(100, 100, 100, 50), batch=self._label_batch),

        'dead': text.Label(
            'DEAD', 
            x=454, y=750, 
            font_size=120, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='top',
            color=(150, 100, 100, 50), batch=self._label_batch),

        'title': text.Label(
            'RAID A DUNGEON', 
            x=454, y=572, 
            font_size=24, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='center',
            color=(100,100,100,255),
            batch=self._label_batch),

        'yourdungeon': text.Label(
            'YOUR DUNGEON (HIT TAB TO EDIT)', 
            x=454, y=100, 
            font_size=24, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='center',
            color=(100,100,100,255),
            batch=self._label_batch),

        # 'wealth': text.Label(
        #     '{}: {} EVIL DOLLARS'.format(self.window.player_data['name'], self.window.player_data['wealth']), 
        #     x=454, y=170, 
        #     font_size=12, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='center', 
        #     color=(100,100,100,255),
        #     batch=self._label_batch),  

        }

        self.header = DungeonListingWidget(
            x=454,
            y=530,
            id=0,
            username='Dungeoneer',
            age='Age', 
            value='Wealth', 
            attempts='Tries', 
            color=(0,0,0,255),
            batch=self._label_batch
        )

        self.page_start = 0

        self.dungeons = self.window.session.dungeons()
        self.dungeons_widgets = []
        # print self.dungeons
        for i in range(self.page_start, min(len(self.dungeons), self.page_start+self.per_page)):

            if self.dungeons[i]['username'] == self.window.player_data['name']:
                self.player_dungeon_widget = DungeonListingWidget(
                    x=454,
                    y=56,
                    id=self.dungeons[i]['id'], 
                    username=self.dungeons[i]['username'], 
                    age=prettydate(int(self.dungeons[i]['age'])),
                    value='${}'.format(self.dungeons[i]['value']),
                    attempts=self.dungeons[i]['attempts'], 
                    batch=self._label_batch
                )
                
                continue


            d = DungeonListingWidget(
                x=454,
                y=500 - (i - self.page_start) * 24,
                id=self.dungeons[i]['id'], 
                username=self.dungeons[i]['username'], 
                age=prettydate(int(self.dungeons[i]['age'])),
                value='${}'.format(self.dungeons[i]['value']),
                attempts=self.dungeons[i]['attempts'], 
                batch=self._label_batch
            )
            self.dungeons_widgets.append(d)
            # self.window.push_handlers(d)

    def update(self, dt):
        pass

    def on_draw(self):
        self.window.clear()
        self._label_batch.draw()
        if self.window.show_fps: 
            self.window.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ENTER:
            # defer(self.window.edit)
            pass
        if symbol == key.TAB:
            m = self.window.load(self.window.player_data['name'])
            if m:
                defer(self.window.edit, m)
            else:
                defer(self.window.edit)
        if symbol == key.R: # Refresh
            defer(self.window.menu)

        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        for d in self.dungeons_widgets + [self.player_dungeon_widget]:
            if not d:
                continue
            if collide.AABB_to_AABB(Point(x,y), 0, 0, Point(d.x, d.y), 800, 24):
                for t in d.labels.values():
                    t.color=(0,0,0,255)
            else:
                for t in d.labels.values():
                    t.color=(100,100,100,255)
    def on_mouse_press(self, x, y, button, modifiers):
        
        for d in self.dungeons_widgets:
            if collide.AABB_to_AABB(Point(x,y), 0, 0, Point(d.x, d.y), 800, 24):
                # defer(self.window.play)
                m = self.window.load(d.username, d.id)
                defer(self.window.play, m)
                # print dungeon
        if self.player_dungeon_widget:
            if collide.AABB_to_AABB(Point(x,y), 0, 0, Point(self.player_dungeon_widget.x, self.player_dungeon_widget.y), 800, 24):
                m = self.window.load(self.window.player_data['name'])
                defer(self.window.edit, m)



    def cleanup(self):
        for d in self.dungeons:
            self.window.remove_handlers(d)