from typing import List, Optional, Tuple, Union

from battlecode25.engine.game.game import Team, UnitType, Direction, MapLocation, RobotInfo, MapInfo, PaintType, GameConstants

# The stubs in this file make it possible for editors to auto-complete the global methods
# They can be imported using "from battlecode25.stubs import *"
# This import is preprocessed away before instrumenting the code

# The dummy implementations in this file exist so that editors won't give warnings like
# "Assigning result of a function call, where the function has no return"

def log(msg: str) -> None:
    """
    Logs a message to the console.
    """
    pass

# GLOBAL QUERY FUNCTIONS

def get_round_num() -> int:
    """
    Returns the current round number, where 1 is the first round of the match
    """
    pass

def get_map_width() -> int:
    """
    Returns the width of the map. Valid x coordinates range from 0 inclusive to width exclusive.
    """
    pass

def get_map_height() -> int:
    """
    Returns the height of the map. Valid y coordinates range from 0 inclusive to height exclusive.
    """
    pass

def get_resource_pattern() -> List[List[bool]]:
    """
    Returns the 5x5 resource pattern. Entry [i][j] is true if the ith row and jth column of the pattern has
    the secondary color.
    """
    pass

def get_tower_pattern(tower_type: UnitType) -> List[List[bool]]:
    """
    Returns the 5x5 tower pattern for the given tower type. Entry [i][j] is true if the ith row and jth column
    of the pattern has the secondary color.
    """
    pass

# ROBOT QUERY FUNCTIONS

def get_id() -> int:
    """
    Returns the ID of this robot.
    """
    pass

def get_team() -> Team:
    """
    Return the robot's team.
    """
    pass

def get_paint() -> int:
    """
    Returns the amount of paint the robot has.
    """
    pass

def get_location() -> MapLocation:
    """
    Returns this robot's current location.
    """
    pass

def get_health() -> int:
    """
    Returns this robot's current health.
    """
    pass

def get_money() -> int:
    """
    Returns the amount of money that this robot's team has.
    """
    pass

def get_type() -> UnitType:
    """
    Returns what type the robot is.
    """
    pass

# SENSING FUNCTIONS

def on_the_map(loc: MapLocation) -> bool:
    """
    Checks whether a MapLocation is on the map.
    """
    pass

def can_sense_location(loc: MapLocation) -> bool:
    """
    Checks whether the given location is withn the robot's vision range and if it is on the map.
    """
    pass

def is_location_occupied(loc: MapLocation) -> bool:
    """
    Checks whether a robot is at the given location. Assumes the location is valid.
    """
    pass

def can_sense_robot_at_location(loc: MapLocation) -> bool:
    """
    Checks whether a robot is at a given location. Assume the location is valid.
    """
    pass

def sense_robot_at_location(loc: MapLocation) -> RobotInfo:
    """
    Senses the robot at the given location, or null if there is no robot there.
    """
    pass

def can_sense_robot(robot_id: int) -> bool:
    """
    Tests whether the given robot exists and if it is within this robot's vision range.
    """
    pass

def sense_robot(robot_id: int) -> RobotInfo:
    """
    Senses information about a particular robot given its ID.
    """
    pass

def sense_nearby_robots(center: MapLocation=None, radius_squared: int=GameConstants.VISION_RADIUS_SQUARED, team: Team=None) -> List[RobotInfo]:
    """
    Returns all robots within vision radius. The objects are returned in no particular order.
    """
    pass

def sense_passability(loc: MapLocation) -> bool:
    """
    Given a senseable location, returns whether that location is passable (a wall).
    """
    pass

def sense_nearby_ruins(radius_squared: int=GameConstants.VISION_RADIUS_SQUARED) -> List[MapLocation]:
    """
    Returns the location of all nearby ruins that are visible to the robot. If radiusSquared is greater than the
    robot's vision radius, uses the robot's vision radius instead.
    """
    pass

def sense_map_info(loc: MapLocation) -> MapInfo: 
    """
    Senses the map info at a location. MapInfo includes walls, paint, marks, and ruins
    """
    pass

def sense_nearby_map_infos(center: MapLocation=None, radius_squared: int=GameConstants.VISION_RADIUS_SQUARED) -> List[MapInfo]:
    """
    Return map info for all senseable locations within a radius squared of a center location. If radiusSquared is 
    larger than the robot's vision radius, uses the robot's vision radius instead
    """
    pass

def get_all_locations_within_radius_squared(center: MapLocation, radius_squared: int) -> List[MapLocation]:
    """
    Returns a list of all locations within the given radiusSquared of a location. If radiusSquared is larger than 
    the robot's vision radius, uses the robot's vision radius instead.
    """
    pass
    
def adjacent_location(direction: Direction) -> MapLocation:
    """
    Returns the location adjacent to current location in the given direction.
    """
    pass

# READINESS FUNCTIONS
    
def is_action_ready() -> bool:
    """
    Tests whether the robot can act.
    """
    pass
    
def get_action_cooldown_turns() -> int:
    """
    Returns the number of action cooldown turns before this unit can act again. When this number is less than 
    GameConstants.COOLDOWN_LIMIT, is_action_ready is true and the robot can act again. This number decreases by
    GameConstants.COOLDOWNS_PER_TURN every turn.
    """
    pass
    
def is_movement_ready() -> bool:
    """
    Tests whether the robot can move.
    """
    pass
    
def get_movement_cooldown_turns() -> int:
    """
    Returns the number of movement cooldown turns before this unit can act again. When this number is less than 
    GameConstants.COOLDOWN_LIMIT, is_action_ready is true and the robot can act again. This number decreases by
    GameConstants.COOLDOWNS_PER_TURN every turn.
    """
    pass

# MOVEMEMENT FUNCTIONS

def can_move(direction: Direction) -> bool:
    """
    Checks whether this robot can move one step in the given direction. Returns false if the robot is not in a mode
    that can move, if the target location is not on the map, if the target location is occupied, if the target 
    location is impassible, or if there are cooldown turns remaining.
    """
    pass

def move(direction: Direction) -> None:
    """
    Moves one step in the given direction
    """
    pass

# ATTACK FUNCTIONS

def can_attack(loc: MapLocation) -> bool:
    """
    Tests whether this robot can attack the given location. Types of attacks for specific units determine whether
    or not towers, other robots, or empty tiles can be attacked. 
    """
    pass

def attack(loc: MapLocation, use_secondary_color: bool=False) -> None:
    """
    Performs the specific attack for this robot type, defaulting to the primary color.
    """
    pass

def can_mop_swing(dir: Direction) -> bool:
    """
    Tests whether this robot (which must be a mopper) can perform a mop swing in a specific direction
    """
    pass

def mop_swing(dir: Direction) -> None:
    """
    Performs a mop swing in the given direction (only for moppers!)
    """
    pass

# MARKING FUNCTIONS
    
def can_mark_tower_pattern(loc: MapLocation, tower_type: UnitType) -> bool:
    """
    Checks if a robot can build a tower by marking a 5x5 pattern centered at the given location.
    This requires there to be a ruin at the location.
    """
    pass
    
def can_mark_resource_pattern(loc: MapLocation) -> bool:
    """
    Checks if the resource pattern can be marked at location
    """
    pass
    
def mark_tower_pattern(loc: MapLocation, tower_type: UnitType) -> None:
    """
    Places markers for the 5x5 pattern corresponding to the given tower type.
    """
    pass

def mark_resource_pattern(loc: MapLocation) -> None:
    """
    Places markers for the resource pattern at the given center location
    """
    pass

def can_mark(loc: MapLocation) -> bool:
    """
    Checks if the location can be marked
    """
    pass

def mark(loc: MapLocation, secondary: bool) -> None:
    """
    Marks the given location with the primary or secondary color for this team
    """
    pass

def can_remove_mark(loc: MapLocation) -> bool: 
    """
    Checks if a mark at the location can be removed
    """
    pass

def remove_mark(loc: MapLocation) -> None:
    """
    Removes the mark at the given location
    """
    pass
    
def can_complete_tower_pattern(loc: MapLocation, tower_type: UnitType) -> bool:
    """
    Checks if the robot can build a tower at the given location. This requires a ruin at the location
    and the tower pattern to be painted correctly.
    """
    pass
    
def complete_tower_pattern(loc: MapLocation, tower_type: UnitType) -> None:
    """
    Builds a tower at the given location
    """
    pass
    
def can_complete_resource_pattern(loc: MapLocation) -> bool:
    """
    Checks if the robot can complete a 5x5 special resource pattern centered at the given location. This
    requires the 5x5 region to be painted correctly.
    """
    pass
    
def complete_resource_pattern(loc: MapLocation) -> None:
    """
    Completes the special resource pattern centered at this location, which it allows it to start being
    counted for extra resources. Even if the pattern is correct, it will not be recognized until this function
    is called.
    """
    pass
        
# BUILDING FUNCTIONS
    
def can_build_robot(robot_type: UnitType, map_location: MapLocation) -> bool:
    """
    Checks if a tower can spawn a robot at the given location. Robots can spawn within a circle of radius sqrt(4)
    of the tower.
    """
    pass

def build_robot(robot_type: UnitType, map_location: MapLocation) -> None:
    """
    Spawns a new robot at the given location.
    """
    pass

# COMMUNICATION FUNCTIONS

def can_send_message(loc: MapLocation) -> bool:
    """
    Returns true if the unit can send a message to a specific location, false otherwise. We can send a message to a location
    if it is within GameConstants.MESSAGE_RADIUS_SQUARED and connected by paint, and only if one unit is a robot and the
    other is a tower.
    """
    pass

def send_message(loc: MapLocation, message_content: int) -> None:
    """
    Sends a 4 byte message to a specific unit at a location on the map. If you send an int larger than 4 bytes, the value will
    be truncated to only include the least significant 4 bytes.
    """
    pass

def read_messages(round=-1) -> List[int]:
    """
    Reads all messages received by this unit within the past 5 rounds if roundNum = -1, or only messages sent from the 
    specified round otherwise
    """
    pass

# TRANSFER PAINT FUNCTIONS

def can_transfer_paint(target_location: MapLocation, amount: int) -> bool:
    """
    Tests whether you can transfer paint to a given robot/tower. You can give paint to an allied robot if you are a mopper
    and can act at the given location. You can give/take paint from allied towers regardless of type, if you can act at the 
    location.
    """
    pass

def transfer_paint(target_location: MapLocation, amount: int) -> None:
    """
    Transfers paint from the robot's stash to the stash of the allied robot or tower at the location.
    """
    pass

# UPGRADE TOWER FUNCTIONS

def can_upgrade_tower(tower_location: MapLocation) -> bool: 
    """
    Checks if a tower can be upgraded by checking conditions on the team, current level, and cost.
    """
    pass

def upgrade_tower(tower_location: MapLocation) -> None: 
    """
    Upgrades the tower to the next level.
    """
    pass

# DEBUG INDICATOR FUNCTIONS

def set_indicator_string(string: str) -> None:
    """
    Sets the indicator string for this robot for debugging purposes. Only the first GameConstants.INDICATOR_STRING_MAX_LENGTH
    characters are used.
    """
    pass

def set_indicator_dot(loc: MapLocation, red: int, green: int, blue: int) -> None:
    """
    Draw a dot on the game map for debugging purposes.
    """
    pass

def set_indicator_line(start_loc: MapLocation, end_loc: MapLocation, red: int, green: int, blue: int) -> None:
    """
    Draw a line on the game map for debugging purposes.
    """
    pass

def set_timeline_marker(label: str, red: int, green: int, blue: int) -> None:
    """
    Adds a marker to the timeline at the current round for debugging purposes. Only the first
    GameConstants.INDICATOR_STRING_MAX_LENGTH characters are used.
    """
    pass

def resign() -> None:
    """
    Causes your team to lose the game. It's like typing "gg."
    """
    pass