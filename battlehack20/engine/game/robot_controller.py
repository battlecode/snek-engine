import random
from .robot import Robot
from .team import Team
from .robot_type import RobotType
from .constants import GameConstants
from .map_location import MapLocation
from .game import Game, Color

#### SHARED METHODS ####

def get_location(robot, game):
    return robot.loc

def get_map_width(game, robot):
    return game.board_width

def get_map_height(game, robot):
    return game.board_height

def get_team(game, robot):
    """
    Return the current robot's team (Team.WHITE or Team.BLACK)
    """
    # TODO change teams to A and B
    return robot.team

def get_type(game, robot):
    return robot.type

def mark(game, robot, loc, color):
    """ 
    loc: MapLocation we want to mark
    color: Color enum specifying the color of the mark
    Marks the specified map location
    """
    game.mark_location(robot.team, loc, color)

def get_pattern(shape):
    """
    shape: Shape enum specifying the shape pattern to retrieve
    Returns a 5 x 5 array of the mark colors
    """
    #TODO: map shape enum to 5x5 array of colors
    return 

def mark_pattern(game, robot, center, shape):
    """
    center: MapLocation center of the 5x5 pattern
    shape: Shape enum to be marked
    Marks the specified pattern centered at the location specified
    """
    #check bounds
    shape_out_of_bounds = (loc.x + 2 >= game.board_width or loc.x - 2 < 0 or loc.y + 2 >= game.board_height or loc.y < 0)
    assert(shape_out_of_bounds, "Shape out of bounds")

    pattern_array = get_pattern(shape)
    for i in range(-2, +3):
        for j in range(-2, +3):
            loc = MapLocation(center.x + i, center.y + j)
            mark(game, robot, loc, pattern_array[i+2][j+2])

def sense(game, robot):
    #TODO adapt this method for new sensing methods
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

def on_the_map(game, robot, loc):
    assert(loc != None, "Not a valid location")
    return game.on_the_map(loc)
    
def assert_can_move(game, robot, dir):
    if dir == None:
        raise RobotError("Not a valid direction")
    if not robot.spawned:
        raise RobotError("Robot is not spawned")
    if robot.movement_cooldown >= GameConstants.COOLDOWN_LIMIT:
        raise RobotError("Robot movement cooldown not yet expired")

    new_location = robot.loc.add(dir)
    if not game.on_the_map(new_location):
        raise RobotError("Robot moved off the map")
    if game.robots[new_location.x][new_location.y] != None:
        raise RobotError("Location is already occupied")
    if not game.is_passable(new_location):
        raise RobotError("Trying to move to an impassable location")

def can_move(game, robot, dir):
    try:
        assert_can_move(game, robot, dir)
        return True
    except RobotError:
        return False

def move(game, robot, dir):
    assert_can_move(game, robot, dir)
    robot.movement_cooldown += GameConstants.COOLDOWN_LIMIT
    robot.loc = robot.loc.add(dir)

#### ATTACK METHODS ####
def assert_can_attack(game, robot, target_location):
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

def can_attack(game, robot, target_location):
    """
    Check if the robot can attack. This function calls `assertAttack`
    and returns a boolean value: True if the attack can proceed, False otherwise.
    """
    try:
        assert_can_attack(game, robot, target_location)
        return True
    except RobotError:
        return False

def attack(game, robot, target_location, attack_type='single'):
    assert_can_attack(game, robot, target_location)
    target = game.robots[target_location.x][target_location.y]
    
    if robot.type == RobotType.SOLDIER:
        if target is None:
            game.paint_tile(target_location, robot.team)
        elif target.team != robot.team:
            if target.type.isTower():
                target.addHealth(-target.attack_strength_1)
        robot.use_paint(robot.type.attack_cost)
        robot.add_action_cooldown(robot.type.action_cooldown)

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

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass