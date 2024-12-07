import random

from .map_info import MapInfo
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
        robot.use_paint(robot.type.attack_cost)
        robot.add_action_cooldown(robot.type.action_cooldown)
        
        if target is None:
            game.paint_tile(target_location, robot.team)
        elif target.team != robot.team:
            if target.type.isTower():
                target.addHealth(-robot.attack_strength_1)

    elif robot.type == RobotType.SPLASHER:
        robot.use_paint(robot.type.attack_cost)
        robot.add_action_cooldown(robot.type.action_cooldown)
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
def assert_spawn(game, robot, robot_type, map_location):
    """
    Assert that the specified robot can spawn a new unit. Raises RobotError if it can't.
    """
    if not game.is_on_board(map_location.x, map_location.y):
        raise RobotError("Build location is out of bounds.")
    
    if game.robots[map_location.x][map_location.y]:
        raise RobotError("Build location is already occupied.")
    
    if robot.type != RobotType.TOWER or not robot.is_action_ready():
        raise RobotError("Robot cannot spawn: it must be a tower and its action cooldown must be ready.")
    
    if robot.paint < robot_type.paint_cost or robot.money < robot_type.money_cost:
        raise RobotError("Insufficient resources: Not enough paint or money to spawn this robot.")


    if not robot.loc.isWithinDistanceSquared(map_location, 3):
        raise RobotError("Target location is out of the tower's spawn radius.")

def can_spawn(game, robot, robot_type, map_location):
    """
    Checks if the specified robot can spawn a new unit.
    Returns True if spawning conditions are met, otherwise False.
    """
    try:
        assert_spawn(robot, robot_type, map_location)
        return True
    except RobotError as e:
        print(f"Build failed: {e}")
        return False

def spawn(game, robot, robot_type, map_location):
    """
    Spawns a new robot of the given type at a specific map location if conditions are met.
    """
    assert_spawn(game, robot, robot_type, map_location)
    game.buildRobot(robot_type, map_location, robot.team)
    robot.set_action_cooldown(10)  # not implemented
    robot.paint -= robot_type.paint_cost
    robot.money -= robot_type.money_cost



## Transferring
def assert_can_transfer_paint(game, robot, target_location, amount):
    if not robot.is_action_ready():
        raise RobotError("Robot cannot attack yet; action cooldown in progress.")
    
    if not game.is_on_board(target_location.x, target_location.y):
        raise RobotError("Target location is not on the map.")
    
    if robot.type != Robot.Type.MOPPER: 
        raise RobotError(f"Robot type is not a Mopper, cannot transfer paint.")
    
    robot_location = MapLocation(robot.row, robot.col)
    distance_squared = robot_location.distanceSquaredTo(target_location)
    if distance_squared > robot.action_radius_squared:
        raise RobotError(f"Target is out of range for {robot.type.name}.")
   
    target = game.get_robot(target_location)
    if target == None: 
        raise RobotError(f"There is no robot at {target_location}.")
    if target.team != robot.team:
        raise RobotError("Moppers can only transfer paint within their own team")
    
    if amount < 0 and target.paint < amount: 
        raise RobotError(f"Target does not have enough paint. Tried to request {-amount}, but target only has {target.paint}")
    if amount >= 0 and robot.paint < amount: 
        raise RobotError(f"Mopper does not have enough paint to transfer.")

def can_transfer_paint(game, robot, target_location, amount):
    try:
        assert_can_transfer_paint(game, robot, target_location, amount)
        return True
    except RobotError as e:
        print(f"Transferring failed: {e}")
        return False

def transfer_paint(game, robot, target_location, amount):
    assert_can_transfer_paint(game, robot, target_location, amount)
    robot.add_paint(-amount)
    target = game.get_robot(target_location)
    target.add_paint(amount)


## Withdrawing
def assert_can_withdraw_paint(game, robot, target_location, amount): 
    if not robot.is_action_ready():
        raise RobotError("Robot cannot attack yet; action cooldown in progress.")
    
    if not game.is_on_board(target_location.x, target_location.y):
        raise RobotError("Target location is not on the map.")
        
    if robot.type != RobotType.MOPPER: 
        raise RobotError(f"Robot type is not a Mopper, cannot transfer paint.")
    
    robot_location = MapLocation(robot.row, robot.col)
    distance_squared = robot_location.distanceSquaredTo(target_location)
    if distance_squared > robot.action_radius_squared:
        raise RobotError(f"Target is out of range for {robot.type.name}.")
    
    target = game.get_robot(target_location)
    if target == None: 
        raise RobotError(f"There is no robot at {target_location}.")
    if target.team != robot.team:
        raise RobotError("Moppers can only transfer paint within their own team")
    if not target.type.isTower():
        raise RobotError(f"The object at {target_location} is not a tower.")

    if amount < 0 and target.paint < amount: 
        raise RobotError(f"Target does not have enough paint. Tried to request {-amount}, but target only has {target.paint}")
    if amount >= 0 and robot.paint < amount: 
        raise RobotError(f"Mopper does not have enough paint to transfer.")


def can_withdraw_paint(game, robot, target_location, amount):
    try:
        assert_can_withdraw_paint(game, robot, target_location, amount)
        return True
    except RobotError as e:
        print(f"Transferring failed: {e}")
        return False

def withdraw_paint(game, robot, target_location, amount):
    assert_can_withdraw_paint(game, robot, target_location, amount)
    robot.add_paint(-amount)
    target = game.get_robot(target_location)
    target.add_paint(amount)



## Upgrading tower 
def assert_can_upgrade_tower(game, team, tower_location): 
    if not game.is_on_board(tower_location.x, tower_location.y):
        raise RobotError("Target location is not on the map.")

    tower = game.get_robot(tower_location)
    if not tower.type.isTower(): 
        raise RobotError("Cannot upgrade a robot that is not a tower,")
    
    if tower.team != team: 
        raise RobotError("Cannot upgrade opposing team's towers.")
    
    if tower.type.level == 3: 
        raise RobotError("Cannot upgrade anymore, tower is already at the maximum level.")
    
    if game.teamInfo.get_coins(team) < tower.type.money_cost: 
        raise RobotError(f"Not enough coins to upgrade the tower")
    

def can_upgrade_tower(game, team, tower_location): 
    try: 
        assert_can_upgrade_tower(game, team, tower_location)
        return True
    except RobotError as e: 
        print(f"Upgrading failed: {e}")
        return False

def upgrade_tower(game, team, tower_location): 
    assert_can_upgrade_tower(game, team, tower_location)
    tower = game.get_robot(tower_location)
    game.teamInfo.add_coins(team, tower.type.money_cost)
    tower.type.upgradeTower(tower)


## Sensing other objects

def assert_can_sense_location(loc):
    pass

def can_sense_location(loc):
    pass


def sense_map_info(game, loc): 
    assert_can_sense_location(loc)
    return game.get_map_info(loc)


def sense_nearby_map_info(game, robot_loc, center, radius_squared):
    assert_can_sense_location(center)

    if radius_squared == -1: 
        radius_squared = GameConstants.VISION_RADIUS_SQUARED

    map_info = []
    for loc in game.get_all_locations_within_radius_squared(center, radius_squared):
        if loc.is_within_distance_squared(robot_loc, GameConstants.VISION_RADIUS_SQUARED):
            map_info.append(game.get_map_info(loc))
    return sorted(map_info)




    



class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass