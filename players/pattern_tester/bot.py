import random

from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!


turn_count = 0
stop = False

directions = [
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
]

def turn():
    global turn_count
    global stop
    turn_count += 1
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    if turn_count <= 10 and can_spawn(RobotType.SOLDIER, spawn_loc):
        spawn(RobotType.SOLDIER, spawn_loc)
    att_dir = get_location().add(directions[random.randint(0, 3)])
    
    dir = directions[random.randint(0, 3)]
    
    # mark_tower_pattern(get_location(), RobotType.LEVEL_ONE_MONEY_TOWER)
    # if turn_count < 20 and can_mark_tower_pattern(get_location(), RobotType.LEVEL_ONE_MONEY_TOWER):
    #     stop = True
    #     mark_tower_pattern(get_location(), RobotType.LEVEL_ONE_MONEY_TOWER)
    if turn_count < 20:
        if can_move(dir) and not stop:
            move(dir)


    

# def turn():

#     """
#     MUST be defined for robot to run
#     This function will be called at the beginning of every turn and should contain the bulk of your robot commands
#     """
#     direction = directions[random.randint(0, 3)]
#     if can_move(direction):
#         move(direction)
