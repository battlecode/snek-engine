import random

from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

directions = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
    Direction.NORTHEAST,
    Direction.NORTHWEST,
    Direction.SOUTHEAST,
    Direction.SOUTHWEST
]

paint_towers = [RobotType.LEVEL_ONE_PAINT_TOWER, RobotType.LEVEL_TWO_PAINT_TOWER, RobotType.LEVEL_THREE_PAINT_TOWER]

def turn():
    loc = get_location()
    log("Location is")
    log(loc)
    # for i in range(9, 14):
    #     for j in range(9, 14):
    #         log(can_sense_location(MapLocation(i, j)))
    log(can_sense_location(MapLocation(-1, -2)))
    log(can_sense_location(MapLocation(-1, 20)))
    log(can_sense_location(MapLocation(15, -2)))
    log(can_sense_location(MapLocation(35, 35)))
    log(can_sense_location(MapLocation(30, 29)))
    log(can_sense_location(MapLocation(29, 25)))
    log()


    # loc = get_location()

    # if can_upgrade_tower(loc):
    #     upgrade_tower(loc)

    # if get_type().is_tower_type():
    #     spawn_loc = loc.add(directions[random.randint(0, 3)])
    #     if can_build_robot(RobotType.SPLASHER, spawn_loc):
    #         build_robot(RobotType.SPLASHER, spawn_loc)

    #     danger = sense_nearby_robots()
    #     log("Nearby robots")
    #     log(danger)
    #     for robot in danger:
    #         if can_attack(robot.get_location()):
    #             attack(robot.get_location())
    
    # else:
    #     dir = directions[random.randint(0, 3)]
    #     if can_move(dir):
    #         move(dir)
    #     attack_loc = get_location().add(dir)
    #     if can_attack(attack_loc):
    #         attack(attack_loc)
