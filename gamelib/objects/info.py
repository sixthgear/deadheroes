from gamelib.objects import player, monsters, devices, tools

class ObjInfo(object):
    def __init__(self, cls, price):
        self.cls = cls
        self.price = price

PLAYER          = 0x00
ZOMBIE          = 0x01
ROBOT           = 0x02
LAUNCHER        = 0x03
MISSILE         = 0x04
DOOR            = 0x80
CHEST           = 0x82
ANVIL           = 0x70

INFO = {
    PLAYER:     ObjInfo(player.Player, 0),
    ZOMBIE:     ObjInfo(monsters.Zombie, 100),
    ROBOT:      ObjInfo(monsters.Robot, 200),
    LAUNCHER:   ObjInfo(monsters.RocketLauncher, 500),
    MISSILE:    ObjInfo(monsters.Rocket, 0),
    DOOR:       ObjInfo(devices.Door, 0),
    CHEST:      ObjInfo(devices.Chest, 0),
    ANVIL:      ObjInfo(devices.Anvil, 200),
}

