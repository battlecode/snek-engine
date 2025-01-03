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

def run_soldier():
    ruins = sense_nearby_ruins()
    loc = get_location()
    if len(ruins) > 0:
        ruin = ruins[0]
        dir = loc.direction_to(ruin)
        if can_move(dir):
            move(dir)
        if can_mark_tower_pattern(ruin, RobotType.LEVEL_ONE_PAINT_TOWER) and sense_map_info(ruin).mark == PaintType.EMPTY:
            mark_tower_pattern(ruin, RobotType.LEVEL_ONE_PAINT_TOWER)
        if can_complete_tower_pattern(ruin, RobotType.LEVEL_ONE_PAINT_TOWER):
            complete_tower_pattern(ruin, RobotType.LEVEL_ONE_PAINT_TOWER)
    map_infos = sense_nearby_map_infos()
    for info in map_infos:
        if info.mark.is_ally() and info.paint == PaintType.EMPTY:
            if can_attack(info.loc):
                attack(info.loc, info.mark.is_secondary)

def run_splasher():
    dir = directions[random.randint(0, 3)]
    if can_move(dir):
        move(dir)
    attack_loc = get_location().add(dir)
    if can_attack(attack_loc):
        attack(attack_loc)

def run_mopper():
    dir = directions[random.randint(0, 3)]
    if can_move(dir):
        move(dir)
    attack_loc = get_location().add(dir)
    if can_attack(attack_loc):
        attack(attack_loc)

def run_robot():
    rtype = get_type()
    if rtype == RobotType.SOLDIER:
        run_soldier()
    elif rtype == RobotType.SPLASHER:
        run_splasher()
    else:
        run_mopper()

def run_tower():
    robot_type = get_round_num() % 3
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    if robot_type == 0 and can_build_robot(RobotType.MOPPER, spawn_loc):
        build_robot(RobotType.MOPPER, spawn_loc)
    if robot_type == 1 and can_build_robot(RobotType.SPLASHER, spawn_loc):
        build_robot(RobotType.SPLASHER, spawn_loc)
    if robot_type == 2 and can_build_robot(RobotType.SOLDIER, spawn_loc):
        build_robot(RobotType.SOLDIER, spawn_loc)

def turn():
    if get_type().is_tower_type():
        run_tower()
    else:
        run_robot()