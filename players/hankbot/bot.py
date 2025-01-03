import random
from battlecode25.stubs import *

directions = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do! 

turn_count = 0

def helper():
    global turn_count
    turn_count += 1
    robot_type = random.randint(0, 2)
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    if robot_type == 0 and can_build_robot(RobotType.MOPPER, spawn_loc):
        build_robot(RobotType.MOPPER, spawn_loc)
    if robot_type == 1 and can_build_robot(RobotType.SPLASHER, spawn_loc):
        build_robot(RobotType.SPLASHER, spawn_loc)
    if robot_type == 2 and can_build_robot(RobotType.SOLDIER, spawn_loc):
        build_robot(RobotType.SOLDIER, spawn_loc)
    att_dir = get_location().add(directions[random.randint(0, 3)])
    if can_attack(att_dir):
        attack(att_dir, use_secondary_color=False)
    dir = directions[random.randint(0, 3)]
    if can_move(dir):
        move(dir)

def turn():
    helper()