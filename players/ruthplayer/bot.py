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
    Direction.NORTHEAST,
    Direction.NORTHWEST,
    Direction.SOUTHEAST,
    Direction.SOUTHWEST
]

paint_towers = [RobotType.LEVEL_ONE_PAINT_TOWER, RobotType.LEVEL_TWO_PAINT_TOWER, RobotType.LEVEL_THREE_PAINT_TOWER]

def turn():
    global turn_count
    found_ruin = 0
    turn_count += 1
    dir = directions[random.randint(0, 3)]

    # if get_type() == RobotType.SPLASHER:
    #     log(get_type())
    #     log(get_paint())
    #     log(get_round_num())
    #     log("")

    if can_upgrade_tower(get_location()):
        upgrade_tower(get_location())

    if get_type() in paint_towers:
        robot_type = turn_count%6
        spawn_loc = get_location().add(directions[random.randint(0, 3)])

        if robot_type == 0 and can_build_robot(RobotType.MOPPER, spawn_loc):
            build_robot(RobotType.MOPPER, spawn_loc)
        if robot_type == 1 and can_build_robot(RobotType.SPLASHER, spawn_loc):
            build_robot(RobotType.SPLASHER, spawn_loc)
        if robot_type == 2 and can_build_robot(RobotType.SOLDIER, spawn_loc):
            build_robot(RobotType.SOLDIER, spawn_loc)
    
    if get_type() == RobotType.SPLASHER:
        # log("splasher here")
        ruins = []

        if not found_ruin and ruins:
            found_ruin = ruins[0]
        
        if found_ruin:
            dir = get_location().direction_to(found_ruin)
            
        if can_attack(get_location()):
            log("about to splash")
            attack(get_location())
            log("splash!")

        if can_move(dir):
            move(dir)

    else:
        if can_move(dir):
            move(dir)

        if can_attack(get_location()):
            attack(get_location())



    
    '''robot_type = random.randint(0, 2)
    spawn_loc = get_location().add(directions[random.randint(0, 3)])
    
    att_dir = get_location().add(directions[random.randint(0, 3)])
    if can_attack(att_dir):
        attack(att_dir, use_secondary_color=False)
    dir = directions[random.randint(0, 3)]
    if can_move(dir):
        move(dir)'''

# def turn():

#     """
#     MUST be defined for robot to run
#     This function will be called at the beginning of every turn and should contain the bulk of your robot commands
#     """
#     # direction = directions[random.randint(0, 3)]
#     # if can_move(direction):
#     #     move(direction)

#     # loc = get_location()
#     # log(loc)

#     move(Direction.NORTH)