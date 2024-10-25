import random
from .robot import Robot
from .team import Team
from .robottype import RobotType
from .constants import GameConstants
from .mapLocation import MapLocation
from .game import Game, Color

#### SHARED METHODS ####
def mark(game, robot, loc, color):
    """ 
    loc: MapLocation we want to mark
    color: Color enum specifying the color of the mark
    Marks the specified map location
    """
    team = get_team(game, robot)
    game.markLocation(team, loc, color)


def get_location(robot, game):
    pass

def get_board_size(game):
    """
    @HQ_METHOD, @PAWN_METHOD

    Return the size of the board (int)
    """
    return game.board_size

def get_team(game, robot):
    """
    @HQ_METHOD, @PAWN_METHOD

    Return the current robot's team (Team.WHITE or Team.BLACK)
    """
    return robot.team

def get_type(game, robot):
    """
    @HQ_METHOD, @PAWN_METHOD

    Return the type of the unit - either RobotType.PAWN or RobotType.OVERLORD
    """
    return robot.type

#### HQ METHODS ####

def get_board(game):
    """
    @HQ_METHOD

    Return the current state of the board as an array of Team.WHITE, Team.BLACK, and None, representing white-occupied,
    black-occupied, and empty squares, respectively.
    """
    board = [[None] * game.board_size for _ in range(game.board_size)]

    for i in range(game.board_size):
        for j in range(game.board_size):
            if game.robots[i][j]:
                board[i][j] = game.robots[i][j].team

    return board

def hq_check_space(game, row, col):
    """
    @HQ_METHOD

    Checks whether a specific board space is occupied and if yes returns the team of the robot occupying the space;
    otherwise returns False. Pawns have a similar method but can only see within their sensory radius
    """
    if not game.robots[row][col]:
        return False
    return game.robots[row][col].team

def spawn(game, robot, row, col):
    """
    @HQ_METHOD

    Spawns a pawn at the given location. Pawns can only be spawned at the edge of the board on your side of the board.
    Only the HQ can spawn units, and it can only spawn one unit per turn.
    :loc should be given as a tuple (row, col), the space to spawn on
    """
    if robot.has_moved:
        raise RobotError('you have already spawned a unit this turn')

    if (robot.team == Team.WHITE and row != 0) or (robot.team == Team.BLACK and row != game.board_size - 1):
        raise RobotError('you can only spawn in the end row of your side of the board')

    if not game.is_on_board(row, col):
        raise RobotError('you cannot spawn a unit on a space that is not on the board')

    if game.robots[row][col]:
        raise RobotError('you cannot spawn a unit on a space that is already occupied')

    game.new_robot(row, col, robot.team, RobotType.PAWN)
    robot.has_moved = True


#### PAWN METHODS ####

def capture(game, robot, new_row, new_col):
    """
    @PAWN_METHOD

    Diagonally capture an enemy piece.
    :new_row, new_col the position of the enemy to capture.
    Units can only capture enemy pieces that are located diagonally left or right in front of them on the board.
    """
    if robot.has_moved:
        raise RobotError('this unit has already moved this turn; robots can only move once per turn')

    row, col = robot.row, robot.col

    if game.robots[row][col] != robot:
        raise RobotError

    if not game.is_on_board(new_row, new_col):
        raise RobotError('you cannot capture a space that is not on the board')

    if not game.robots[new_row][new_col]:
        raise RobotError('you cannot capture an empty space')

    if game.robots[new_row][new_col].team == robot.team:
        raise RobotError('you cannot capture your own piece')

    if abs(col - new_col) != 1:
        raise RobotError('you must capture diagonally')

    if (robot.team == Team.WHITE and row - new_row != -1) or (robot.team == Team.BLACK and row - new_row != 1):
        raise RobotError('you must capture diagonally forwards')

    captured_robot = game.robots[new_row][new_col]

    game.delete_robot(captured_robot.id)
    game.robots[row][col] = None

    robot.row = new_row
    robot.col = new_col

    game.robots[new_row][new_col] = robot
    robot.has_moved = True

def get_location(game, robot):
    """
    @PAWN_METHOD

    Return the current location of the robot
    """
    row, col = robot.row, robot.col
    if game.robots[row][col] != robot:
        raise RobotError('something went wrong; please contact the devs')
    return row, col

def move_forward(game, robot):
    """
    @PAWN_METHOD

    Move the current unit forward. A unit can only be moved if there is no unit already occupying the space.
    """
    if robot.has_moved:
        raise RobotError('this unit has already moved this turn; robots can only move once per turn')

    row, col = robot.row, robot.col
    if game.robots[row][col] != robot:
        raise RobotError('something went wrong; please contact the devs')

    if robot.team == Team.WHITE:
        new_row, new_col = row + 1, col
    else:
        new_row, new_col = row - 1, col

    if not game.is_on_board(new_row, new_col):
        raise RobotError('you cannot move to a space that is not on the board')

    if game.robots[new_row][new_col]:
        raise RobotError('you cannot move to a space that is already occupied')

    game.robots[row][col] = None

    robot.row = new_row
    robot.col = new_col
    game.robots[new_row][new_col] = robot
    robot.has_moved = True

def pawn_check_space(game, robot, row, col):
    """
    @PAWN_METHOD

    Checks whether a specific board space is occupied and if yes returns the team of the robot occupying the space;
    otherwise returns False.

    Raises a RobotError if the space is not within the sensory radius

    HQs have a similar method but can see the full board
    """
    if game.robots[robot.row][robot.col] != robot:
        raise RobotError('something went wrong; please contact the devs')

    drow, dcol = abs(robot.row - row), abs(robot.col - col)
    if max(drow, dcol) > 2:
        raise RobotError('that space is not within sensory radius of this robot')

    if not game.robots[row][col]:
        return False
    return game.robots[row][col].team

def sense(game, robot):
    """
    @PAWN_METHOD

    Sense nearby units; returns a list of tuples of the form (row, col, robot.team) within sensor radius of this robot (excluding yourself)
    You can sense another unit other if it is within sensory radius of you; e.g. max(|robot.x - other.x|, |robot.y - other.y|) <= sensory_radius
    """
    row, col = robot.row, robot.col

    robots = []

    for i in range(-game.sensor_radius, game.sensor_radius + 1):
        for j in range(-game.sensor_radius, game.sensor_radius + 1):
            if i == 0 and j == 0:
                continue

            new_row, new_col = row + i, col + j
            if not game.is_on_board(new_row, new_col):
                continue

            if game.robots[new_row][new_col]:
                robots.append((new_row, new_col, game.robots[new_row][new_col].team))

    return robots

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass