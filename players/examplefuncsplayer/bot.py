import random

from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

turn_count = 0
rng = random.Random(6147)
directions = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]

def turn():
    robot_type = rng.randint(0, 2)
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    if robot_type == 0 and can_spawn(RobotType.SOLDIER, spawn_loc):
        spawn(RobotType.SOLDIER, spawn_loc)
    elif robot_type == 1 and can_spawn(RobotType.MOPPER,spawn_loc):
        spawn(RobotType.MOPPER, spawn_loc)
    elif robot_type == 2 and can_spawn(robot_type=RobotType.SPLASHER, map_location=spawn_loc):
        spawn(RobotType.SPLASHER, spawn_loc)
    move_dir = directions[random.randint(0, 3)]
    att_dir = get_location().add(directions[random.randint(0, 3)])
    #if can_move(move_dir):
        #move(move_dir)
    #if can_attack(att_dir):
        #attack(att_dir, use_secondary_color=False)


# def turn():

#     """
#     MUST be defined for robot to run
#     This function will be called at the beginning of every turn and should contain the bulk of your robot commands
#     """
#     direction = DIRECTIONS[random.randint(0, 3)]
#     if can_move(direction):
#         move(direction)



