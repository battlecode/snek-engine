import random

# from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
# instrument()

def turn():
    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    # direction = directions[random.randint(0, 3)]

    # if can_move(direction):
        # move(direction)

    loc = get_location()
    # log(str(loc))


'''
 0           0 RESUME                   0

  1           2 LOAD_CONST               0 (0)
              4 PUSH_NULL
              6 LOAD_NAME                5 (instrument)
              8 CALL                     0
             10 CACHE                    0 (counter: 17)
             12 CACHE                    0 (func_version: 0)
             14 CACHE                    0
             16 POP_TOP

             
 0           0 RESUME                   0

  1           2 LOAD_CONST               0 (0)
              4 PUSH_NULL
              6 LOAD_NAME                2 (instrument)
              8 CALL                     0
             10 CACHE                    0 (counter: 17)
             12 CACHE                    0 (func_version: 0)
             14 CACHE                    0

 25          16 POP_TOP
'''