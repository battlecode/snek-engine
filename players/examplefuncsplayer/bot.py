import random

from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!


turn_count = 0

directions = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]

def turn():
    global turn_count
    turn_count += 1
    robot_type = random.randint(0, 2)
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    if robot_type == 0 and can_spawn(RobotType.MOPPER, spawn_loc):
        spawn(RobotType.MOPPER, spawn_loc)
    if robot_type == 1 and can_spawn(RobotType.SPLASHER, spawn_loc):
        spawn(RobotType.SPLASHER, spawn_loc)
    if robot_type == 2 and can_spawn(RobotType.SOLDIER, spawn_loc):
        spawn(RobotType.SOLDIER, spawn_loc)
    att_dir = get_location().add(directions[random.randint(0, 3)])
    if can_attack(att_dir):
        attack(att_dir, use_secondary_color=False)
    
    dir = directions[random.randint(0, 3)]
    if can_move(dir):
        move(dir)


# def turn():

#     """
#     MUST be defined for robot to run
#     This function will be called at the beginning of every turn and should contain the bulk of your robot commands
#     """
#     direction = directions[random.randint(0, 3)]
#     if can_move(direction):
#         move(direction)



