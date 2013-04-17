from gamelib.objects import player, monsters, devices, tools

PLAYER          = 0x00
ZOMBIE          = 0x01
ROBOT           = 0x02
LAUNCHER        = 0x03
MISSILE         = 0x04
DOOR            = 0x80
CHEST           = 0x82

INFO = {
    PLAYER:     player.Player,
    ZOMBIE:     monsters.Zombie,
    ROBOT:      monsters.Robot,
    LAUNCHER:   monsters.RocketLauncher,
    MISSILE:    monsters.Rocket,
    DOOR:       devices.Door,
    CHEST:      devices.Chest,
}