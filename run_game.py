#! /usr/bin/env python -O
import sys
sys.path.insert(0,'lib')

import pyglet
pyglet.options['debug_gl'] = False
pyglet.resource.path = ['data']
pyglet.resource.reindex()

if not pyglet.media.have_avbin:    
    print 'You need to install AVbin http://avbin.github.io to play this game.'
    sys.exit()

# run game
from gamelib.controller import controller
c = controller.Controller()    
c.run()

# import cProfile
# cProfile.run('c.run()', 'go.log-cprofile')