import random

from .map_info import MapInfo
from .robot import Robot
from .team import Team
from .robot_type import RobotType
from .constants import GameConstants
from .map_location import MapLocation
from .direction import Direction

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
    assert loc != None, "Not a valid location"
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
def assert_can_attack(game, robot, loc):
    """
    Assert that the robot can attack. This function checks all conditions necessary
    for the robot to perform an attack and raises an error if any are not met.
    """
    if loc is None and not robot.type.is_tower():
        raise ValueError("Location cannot be None unless the unit is a tower.")
    if not robot.is_action_ready():
        raise ValueError("Action cooldown is in progress.")
    if game.is_setup_phase():
        raise ValueError("Cannot attack during setup phase.")

    if robot.type == RobotType.SOLDIER:
        if loc is not None:
            if not loc.is_within_distance_squared(robot.loc, robot.type.action_radius_squared):
                raise ValueError("Target location is out of action range.")
            if robot.paint < robot.type.attack_cost:
                raise ValueError("Insufficient paint to perform attack.")
    elif robot.type == RobotType.SPLASHER:
        if loc is not None:
            if not loc.is_within_distance_squared(robot.loc, robot.type.action_radius_squared):
                raise ValueError("Target location is out of action range.")
            if robot.paint < robot.type.attack_cost:
                raise ValueError("Insufficient paint to perform attack.")
    elif robot.type == RobotType.MOPPER:
        if loc is not None:
            if not loc.is_within_distance_squared(robot.loc, robot.type.action_radius_squared):
                raise ValueError("Target location is out of action range.")
            if robot.paint < robot.type.attack_cost:
                raise ValueError("Insufficient paint to perform attack.")
    else:  # Tower
        if loc is None:
            if robot.has_tower_area_attacked:
                raise ValueError("Tower has already performed an area attack.")
        else:
            if robot.has_tower_single_attacked:
                raise ValueError("Tower has already performed a single attack.")
            if not loc.is_within_distance_squared(robot.loc, robot.type.action_radius_squared):
                raise ValueError("Target location is out of action range.")

def can_attack(game, robot, loc):
    """
    Check if the robot can attack. This function calls `assertAttack`
    and returns a boolean value: True if the attack can proceed, False otherwise.
    """
    try:
        assert_can_attack(game, robot, loc)
        return True
    except RobotError:
        return False

def attack(robot, game, loc, use_secondary_color=False):
    assert_can_attack(robot, game, loc)
    robot.add_action_cooldown(robot.type.action_cooldown)

    if robot.type == RobotType.SOLDIER:
        paint_type = game.get_secondary_paint(robot.team) if use_secondary_color else game.get_primary_paint(robot.team)
        robot.use_paint(robot.type.attack_cost)

        target_robot = game.get_robot(loc)
        if target_robot and target_robot.type.is_tower() and target_robot.team != robot.team:
            target_robot.add_health(-robot.type.attack_strength)
        else:
            if game.get_paint(loc) == 0 or game.team_from_paint(paint_type) == game.team_from_paint(game.get_paint(loc)):
                game.set_paint(loc, paint_type)

    elif robot.type == RobotType.SPLASHER:
        paint_type = game.get_secondary_paint(robot.team) if use_secondary_color else game.get_primary_paint(robot.team)
        robot.use_paint(robot.type.attack_cost)

        all_locs = game.get_all_locations_within_radius_squared(loc, robot.type.action_radius_squared)
        for new_loc in all_locs:
            target_robot = game.get_robot(new_loc)
            if target_robot and target_robot.type.is_tower() and target_robot.team != robot.team:
                target_robot.add_health(-robot.type.attack_strength)
            else:
                if game.get_paint(new_loc) == 0 or game.team_from_paint(paint_type) == game.team_from_paint(game.get_paint(new_loc)):
                    game.set_paint(new_loc, paint_type)

    elif robot.type == RobotType.MOPPER:
        if loc is None:
            mop_swing(robot, game, loc) 
        else:
            paint_type = game.get_secondary_paint(robot.team) if use_secondary_color else game.get_primary_paint(robot.team)
            robot.use_paint(robot.type.attack_cost)
            
            target_robot = game.get_robot(loc)
            if target_robot and target_robot.type.is_robot_type(target_robot.type) and target_robot.team != robot.team:
                target_robot.add_paint(-GameConstants.MOPPER_ATTACK_PAINT_DEPLETION) # add game constant
                robot.add_paint(GameConstants.MOPPER_ATTACK_PAINT_ADDITION) # add game constant

            if game.team_from_paint(paint_type) != game.team_from_paint(game.get_paint(loc)):
                game.set_paint(loc, 0)

    else:  # Tower
        if loc is None:
            robot.has_tower_area_attacked = True
            all_locs = game.get_all_locations_within_radius_squared(robot.loc, robot.type.action_radius_squared)
            for new_loc in all_locs:
                target_robot = game.get_robot(new_loc)
                if target_robot and target_robot.team != robot.team:
                    target_robot.add_health(-robot.type.aoe_attack_strength)
        else:
            robot.has_tower_single_attacked = True
            target_robot = game.get_robot(loc)
            if target_robot and target_robot.team != robot.team:
                target_robot.add_health(-robot.type.attack_strength)

def mop_swing(robot, game, direction):
    assert robot.type == RobotType.MOPPER
    assert direction in [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
    dx = [[-1, 0, 1], [-1, 0, 1], [1, 1, 1], [-1, -1, -1]]
    dy = [[1, 1, 1], [-1, -1, -1], [-1, 0, 1], [-1, 0, 1]]

    dir_idx = 0
    if dir == Direction.SOUTH:
        dir_idx = 1
    elif dir == Direction.EAST:
        dir_idx = 2
    elif dir == Direction.WEST:
        dir_idx = 3

    for i in range(3):
        x = self.get_location().x + dx[dir_idx][i]
        y = self.get_location().y + dy[dir_idx][i]
        new_loc = MapLocation(x, y)
    
        if not game.on_the_map(new_loc):
            continue
    
    
        robot = game.get_robot(new_loc)
        if robot and robot.team != robot.team:
            if self.team != robot.get_team():
                robot.add_paint(-GameConstants.MOPPER_SWING_PAINT_DEPLETION)

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

def assert_can_send_message(game, robot, loc):
    pass

def can_send_message(game, robot, loc):
    pass

def get_messages(game, robot, round):
    pass

def get_messages(game, robot):
    pass



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