import random

from battlecode25.stubs import *

# This is an example bot written by the developers!
# Use this to help write your own code, or run it against your bot to see how well you can do!

directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]

def turn():

    """
    MUST be defined for robot to run
    This function will be called at the beginning of every turn and should contain the bulk of your robot commands
    """
    direction = directions[random.randint(0, 3)]
    if can_move(direction):
        move(direction)
