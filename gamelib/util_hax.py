import pyglet

def defer(func, *args, **kwargs):
    """
    I'm almost sorry.
    """
    pyglet.clock.schedule_once(lambda dt: func(*args, **kwargs), 0.0)
