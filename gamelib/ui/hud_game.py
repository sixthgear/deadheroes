import pyglet
from pyglet import text
from pyglet.gl import *

class HUD(object):

    def __init__(self):

        vertices = []
        colors = []

        
        vertices += self.rect(14, 750, 50, 786)
        vertices += self.rect(58, 750, 94, 786)
        vertices += self.rect(102, 750, 138, 786)
        
        colors += [1, 1, 1] * 12

        self._vertex_list = pyglet.graphics.vertex_list(len(vertices)/2, 'v2f', 'c3f')
        self._vertex_list.vertices = vertices
        self._vertex_list.colors = colors
        self._label_batch = pyglet.graphics.Batch()

        self.labels = {
            'money': text.Label(
                '0 EVIL DOLLARS', 
                x=160, y=768, 
                font_size=12, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='center', 
                color=(100,100,100,255),
                batch=self._label_batch),  

            'gameover': text.Label(
                'YOU WIN', 
                x=640, y=384, 
                font_size=48, font_name='DYLOVASTUFF', anchor_x='center', anchor_y='center',
                color=(100,100,100,0),
                batch=self._label_batch),

            'instructions': text.Label(
                'PRESS SPACE TO TRY AGAIN.', 
                x=640, y=336, 
                font_size=18, font_name='DYLOVASTUFF', anchor_x='center', anchor_y='center',
                color=(100,100,100,0),
                batch=self._label_batch),

            # 'done': text.Label(
            #     'DONE', 
            #     x=1244, y=768, 
            #     font_size=12, font_name="Arial", anchor_x='right', anchor_y='center',  
            #     color=(100,100,100,255),
            #     batch=self._label_batch),
            'z': text.Label('Z', x=32, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
            'x': text.Label('X', x=76, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
            'c': text.Label('C', x=120, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
        }

    def alter_budget(self, budget):
        self.labels['money'].text = '{} EVIL DOLLARS'.format(budget)

    def title(self, name):
        self.labels['gameover'].text = '{}\'S EVIL DUNGEON'.format(name.upper()) 
        self.labels['instructions'].text = 'GET TO THE CHEST, GET OUT WITH THE MONEY.'
        self.labels['gameover'].color=(100,100,100,255)
        self.labels['instructions'].color=(100,100,100,255)

    def play(self):
        self.labels['gameover'].color=(100,100,100,0)
        self.labels['instructions'].color=(100,100,100,0)        

    def gameover(self, won=True):
        if won:
            self.labels['gameover'].text = 'CONGRATULATIONS JERK.'
            self.labels['instructions'].text = 'YOU STOLE $500. PRESS ESC TO RETURN TO MENU.'
        else:
            self.labels['gameover'].text = 'YOU ARE DEAD.'
            self.labels['instructions'].text = 'PRESS SPACE TO TRY AGAIN OR ESC TO RETURN TO MENU.'

        self.labels['gameover'].color=(100,100,100,255)
        self.labels['instructions'].color=(100,100,100,255)

    def validated(self, won=True):
        if won:
            self.labels['gameover'].text = 'AWW YEAAH, DUNGEON VALIDATED.'
            self.labels['instructions'].text = ' PRESS ESC TO RETURN TO EDITOR.'
        else:
            self.labels['gameover'].text = 'YOU ARE DEAD.'
            self.labels['instructions'].text = 'AND YOUR DUNGEON SUCKS. PRESS SPACE TO TRY AGAIN OR ESC TO RETURN TO EDITOR.'

        self.labels['gameover'].color=(100,100,100,255)
        self.labels['instructions'].color=(100,100,100,255)        

    def rect(self, x0, y0, x1, y1):
        return [x0, y0, x0, y1, x1, y1, x1, y0]        

    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glColor4f(1,1,1,1)
        self._vertex_list.draw(GL_QUADS)
        
        self._label_batch.draw()
