import random
from .robot import Robot
from .team import Team
from .robottype import RobotType
from .constants import GameConstants
from .map_location import MapLocation

#### SHARED METHODS ####

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

#### ATTACK METHODS ####
def assertAttack(game, robot, target_location):
    """
    Assert that the robot can attack. This function checks all conditions necessary
    for the robot to perform an attack and raises an error if any are not met.
    """
    if not robot.is_action_ready():
        raise RobotError("Robot cannot attack yet; action cooldown in progress.")

    if not game.is_on_board(target_location.x, target_location.y):
        raise RobotError("Target location is not on the map.")

    required_paint = robot.max_paint
    if robot.paint < required_paint:
        raise RobotError(f"Not enough paint. Requires {required_paint}, but only has {robot.paint}.")
    
    if robot.type in [RobotType.SOLDIER, RobotType.SPLASHER, RobotType.MOPPER]:
        robot_location = MapLocation(robot.row, robot.col)
        distance_squared = robot_location.distanceSquaredTo(target_location)
        if distance_squared > robot.attack_range_squared:
            raise RobotError(f"Target is out of range for {robot.type.name}.")
    if robot.type == RobotType.SOLDIER:
        target = game.robots.get((target_location.x, target_location.y))
        if target and target.team != robot.team and target.type != RobotType.TOWER:
            raise RobotError("Soldiers can only attack towers.")

def canAttack(game, robot, target_location):
    """
    Check if the robot can attack. This function calls `assertAttack`
    and returns a boolean value: True if the attack can proceed, False otherwise.
    """
    try:
        assertAttack(game, robot, target_location)
        return True
    except RobotError:
        return False


def attack(game, robot, target_location, attack_type='single'):
    assertAttack(game, robot, target_location)
    target = game.robots[target_location.x][target_location.y]
    
    robot_location = MapLocation(robot.row, robot.col)
    distance_squared = robot_location.distanceSquaredTo(target_location)

    if robot.type == RobotType.SOLDIER:
        if target is None:
            game.paint_tile(target_location, robot.team)
        elif target.team != robot.team:
            target.health -= 20 if target.type == RobotType.TOWER else 0
        robot.use_paint(5)
        robot.set_action_cooldown(10) # not implemented

    elif robot.type == RobotType.SPLASHER:
        radius = 2
        robot.use_paint(50)
        robot.set_action_cooldown(50) # not implemented
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                splash_location = target_location.translate(dx, dy)
                if game.is_on_board(splash_location.x, splash_location.y):
                    splash_target = game.robots[splash_location.x][splash_location.y]
                    if splash_target is None:
                        game.paint_tile(splash_location, robot.team)
                    elif splash_target.team != robot.team and splash_target.type == RobotType.TOWER:
                        splash_target.health -= 50

    elif robot.type == RobotType.MOPPER:
        if attack_type == 'single':
            if target and target.team != robot.team:
                paint_siphoned = min(10, target.paint)
                target.use_paint(paint_siphoned)
                robot.add_paint(paint_siphoned // 2)
            else:
                game.remove_enemy_paint(target_location)
            robot.set_action_cooldown(30) # not implemented

        elif attack_type == 'aoe':
            robot.set_action_cooldown(40) # not implemented
            best_direction = None
            max_enemy_count = 0
            direction_vectors = [(1, 0), (0, 1), (-1, 0), (0, -1)] 

            for dx, dy in direction_vectors:
                enemy_count = 0
                for i in range(1, 4): 
                    swing_location = target_location.translate(i * dx, i * dy)
                    if game.is_on_board(swing_location.x, swing_location.y):
                        swing_target = game.robots[swing_location.x][swing_location.y]
                        if swing_target and swing_target.team != robot.team:
                            enemy_count += 1
                        else:
                            break 
                    else:
                        break  

                if enemy_count > max_enemy_count:
                    max_enemy_count = enemy_count
                    best_direction = (dx, dy)

            if best_direction is not None:
                dx, dy = best_direction
                for i in range(1, 4):
                    swing_location = target_location.translate(i * dx, i * dy)
                    if game.is_on_board(swing_location.x, swing_location.y):
                        swing_target = game.robots[swing_location.x][swing_location.y]
                        if swing_target and swing_target.team != robot.team:
                            swing_target.use_paint(min(5, swing_target.paint))

    elif robot.type == RobotType.TOWER:
        if attack_type == 'single':
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    target_loc = MapLocation(robot.row + dx, robot.col + dy)
                    if game.is_on_board(target_loc.x, target_loc.y):
                        target_robot = game.robots[target_loc.x][target_loc.y]
                        if target_robot and target_robot.team != robot.team:
                            target_robot.health -= 20
                            if target_robot.health <= 0:
                                game.delete_robot(target_robot.id)
                        break
                else:
                    continue
                break
        elif attack_type == 'aoe':
            aoe_radius_squared = robot.aoe_attack_range_squared
            center = MapLocation(robot.row, robot.col)
            nearby_locations = game.getAllLocationsWithinRadiusSquared(center, aoe_radius_squared)

            for loc in nearby_locations:
                if game.is_on_board(loc.x, loc.y):
                    target_robot = game.robots[loc.x][loc.y]
                    if target_robot and target_robot.team != robot.team:
                        target_robot.health -= 10
                        if target_robot.health <= 0:
                            game.delete_robot(target_robot.id)

# SPAWN METHODS
def assert_spawn(robot, robot_type, map_location):
    """
    Assert that the specified robot can spawn a new unit. Raises RobotError if it can't.
    """
    if robot.type != RobotType.TOWER or not robot.is_action_ready():
        raise RobotError("Robot cannot spawn: it must be a tower and its action cooldown must be ready.")
    
    if robot.paint < robot_type.paint_cost or robot.money < robot_type.money_cost:
        raise RobotError("Insufficient resources: Not enough paint or money to spawn this robot.")
    
    spawn_radius = 5
    if abs(robot.row - map_location.row) > spawn_radius // 2 or abs(robot.col - map_location.col) > spawn_radius // 2:
        raise RobotError("Target location is out of the tower's spawn radius.")

def can_spawn(robot, robot_type, map_location):
    """
    Checks if the specified robot can spawn a new unit.
    Returns True if spawning conditions are met, otherwise False.
    """
    try:
        assert_spawn(robot, robot_type, map_location)
        return True
    except RobotError as e:
        print(f"Spawn failed: {e}")
        return False

def assert_build(game, map_location):
    """
    Assert that a robot can be built at the specified map location.
    Raises RobotError if the location is invalid or occupied.
    """
    if not game.is_on_board(map_location.row, map_location.col):
        raise RobotError("Build location is out of bounds.")
    
    if game.robots[map_location.row][map_location.col]:
        raise RobotError("Build location is already occupied.")

def can_build(game, map_location):
    """
    Checks if a new robot can be built at the specified map location.
    Returns True if the location is valid and unoccupied, otherwise False.
    """
    try:
        assert_build(game, map_location)
        return True
    except RobotError as e:
        print(f"Build failed: {e}")
        return False

def spawn(game, robot, robot_type, map_location):
    """
    Spawns a new robot of the given type at a specific map location if conditions are met.
    """
    assert_spawn(robot, robot_type, map_location)
    assert_build(game, map_location)
    buildRobot(game, robot_type, map_location, robot.team)
    robot.set_action_cooldown(10)  # not implemented
    robot.paint -= robot_type.paint_cost
    robot.money -= robot_type.money_cost

def buildRobot(game, robot_type, map_location, team):
    """
    Creates and places a new robot of the specified type at the given map location.
    """
    new_robot = Robot(map_location.row, map_location.col, team, game.robot_count, robot_type)
    game.add_robot(new_robot)

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass