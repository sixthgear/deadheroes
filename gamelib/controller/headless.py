import array
# from gamelib.controller import play
from gamelib.controller import replay
from gamelib.objects import player
from gamelib import map

DT = 1 / 60.0
DT2 = DT * DT

def run():    
    m = map.Map.load(0)
    rep = replay.Replay.load('replay.rep', dungeon=m)
    while rep.update(DT2) == 1:
        pass

    
