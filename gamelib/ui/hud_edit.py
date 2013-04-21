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

            'wealth': text.Label(
                '0 EVIL DOLLARS', 
                x=160, y=768, 
                font_size=14, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='bottom', 
                color=(20,20,20,255),
                batch=self._label_batch),  

            'budget': text.Label(
                '0 EVIL DOLLARS', 
                x=160, y=768, 
                font_size=12, font_name='DYLOVASTUFF', anchor_x='left', anchor_y='top', 
                color=(100,0,0,255),
                batch=self._label_batch),  

            'title': text.Label(
                'DESIGN YOUR DUNGEON', 
                x=640, y=768, 
                font_size=24, font_name='DYLOVASTUFF', anchor_x='center', anchor_y='center',
                color=(100,100,100,255),
                batch=self._label_batch),

            'done': text.Label(
                'DONE', 
                x=1244, y=768, 
                font_size=12, font_name='DYLOVASTUFF', anchor_x='right', anchor_y='center',  
                color=(100,100,100,255),
                batch=self._label_batch),
            'q': text.Label('Q', x=32, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
            'w': text.Label('W', x=76, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
            'e': text.Label('E', x=120, y=768, anchor_x='center', anchor_y='center', font_size=12, font_name='DYLOVASTUFF', color=(0,0,0,255), batch=self._label_batch),
        }

    def alter_budget(self, budget, wealth):
        self.labels['wealth'].text = 'WEALTH: {} EVIL DOLLARS'.format(wealth)
        if budget < 0:
            self.labels['budget'].text = 'BUDGET: +{} EVIL DOLLARS'.format(abs(budget))
            self.labels['budget'].color=(0,100,0,255) 
        else:
            self.labels['budget'].text = 'BUDGET: ({}) EVIL DOLLARS'.format(budget)
            self.labels['budget'].color=(100,0,0,255) 


    def rect(self, x0, y0, x1, y1):
        return [x0, y0, x0, y1, x1, y1, x1, y0]        

    def draw(self):
        glDisable(GL_TEXTURE_2D)
        glColor4f(1,1,1,1)
        self._vertex_list.draw(GL_QUADS)
        
        self._label_batch.draw()
