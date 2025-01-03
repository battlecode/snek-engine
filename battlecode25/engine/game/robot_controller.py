from __future__ import annotations
from .robot import Robot
from .robot_type import RobotType
from .constants import GameConstants
from .map_location import MapLocation
from .direction import Direction
from .shape import Shape
from .domination_factor import DominationFactor
from .team import Team
from typing import List
from .robot_info import RobotInfo
from .map_info import MapInfo

#Imported for type checking
if 1 == 0:
    from .game import Game

#### SHARED METHODS ####

class RobotController:

    def __init__(self, game: Game, robot: Robot):
        self.game = game
        self.robot = robot

    # INTERNAL HELPERS

    def assert_not_none(self, o) -> None:
        if o is None:
            raise RobotError("Argument has invalid None value")

    def assert_can_act_location(self, loc, max_radius_squared) -> None:
        self.assert_not_none(loc)
        if self.robot.loc.distance_squared_to(loc) > max_radius_squared:
            raise RobotError("Target location is not within action range")
        if not self.game.on_the_map(loc):
            raise RobotError("Target location is not on the map")
        
    def assert_is_robot_type(self, type: RobotType) -> None:
        if not type.is_robot_type():
            raise RobotError("Towers cannot perform this action")
        
    def assert_is_tower_type(self, type: RobotType) -> None:
        if not type.is_tower_type():
            raise RobotError("Robots cannot perform this action")

    # GLOBAL QUERY FUNCTIONS

    def get_round_num(self) -> int:
        return self.game.round

    def get_map_width(self) -> int:
        return self.game.width

    def get_map_height(self) -> int:
        return self.game.height
    
    def get_resource_pattern(self) -> List[List[bool]]:
        return self.game.pattern[Shape.RESOURCE.value]
    
    def get_tower_pattern(self, tower_type: RobotType) -> List[List[bool]]:
        self.assert_is_tower_type(tower_type)
        return self.game.pattern[self.game.shape_from_tower_type(tower_type).value]
    
    # ROBOT QUERY FUNCTIONS

    def get_id(self) -> int:
        return self.robot.id

    def get_team(self) -> Team:
        """
        Return the current robot's team (Team.A or Team.B)
        """
        return self.robot.team
    
    def get_paint(self) -> int:
        return self.robot.paint
    
    def get_location(self) -> MapLocation:
        return self.robot.loc
    
    def get_health(self) -> int:
        return self.robot.health
    
    def get_money(self) -> int:
        return self.game.team_info.get_coins(self.robot.team)

    def get_type(self) -> RobotType:
        return self.robot.type

    # SENSING FUNCTIONS

    def on_the_map(self, loc: MapLocation) -> bool:
        self.assert_not_none(loc)
        return self.game.on_the_map(loc)

    def assert_can_sense_location(self, loc: MapLocation) -> None:
        self.assert_not_none(loc)
        if not self.game.on_the_map(loc):
            raise RobotError("Target location is not on the map")
        if self.robot.loc.distance_squared_to(loc) > GameConstants.VISION_RADIUS_SQUARED:
            raise RobotError("Target location is out of vision range")

    def can_sense_location(self, loc: MapLocation) -> bool:
        try:
            self.assert_can_sense_location(loc)
            return True
        except RobotError:
            return False

    def is_location_occupied(self, loc: MapLocation) -> bool:
        self.assert_can_sense_location(loc)
        return self.game.get_robot(loc) is not None

    def can_sense_robot_at_location(self, loc: MapLocation) -> bool:
        try:
            return self.is_location_occupied(loc)
        except RobotError:
            return False

    def sense_robot_at_location(self, loc: MapLocation) -> RobotInfo:
        self.assert_can_sense_location(loc)
        robot = self.game.get_robot(loc)
        return None if robot is None else robot.get_robot_info()   

    def can_sense_robot(self, robot_id: int) -> bool:
        sensed_robot = self.game.get_robot_by_id(robot_id)
        return sensed_robot is not None and self.can_sense_location(sensed_robot.loc)

    def sense_robot(self, robot_id: int) -> RobotInfo:
        if not self.can_sense_robot(robot_id):
            raise RobotError("Cannot sense robot; It may be out of vision range not exist")
        return self.game.get_robot_by_id(robot_id).get_robot_info()
    
    def assert_radius_non_negative(self, radius: int) -> None:
        if radius < 0:
            raise RobotError("Radius is negative")

    def sense_nearby_robots(self, center: MapLocation=None, radius_squared: int=GameConstants.VISION_RADIUS_SQUARED, team: Team=None) -> List[RobotInfo]:
        if center is None:
            center = self.robot.loc
        self.assert_radius_non_negative(radius_squared)

        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)
        sensed_locs = self.game.get_all_locations_within_radius_squared(center, radius_squared)
        result = []
        for loc in sensed_locs:
            sensed_robot = self.game.get_robot(loc)
            if sensed_robot == self.robot:
                continue
            if not self.can_sense_location(sensed_robot.loc):
                continue
            if team is not None and sensed_robot.team != team:
                continue
            result.append(sensed_robot.get_robot_info())
        return result
    
    def sense_passability(self, loc: MapLocation) -> bool:
        self.assert_can_sense_location(loc)
        return self.game.is_passable(loc)
    
    def sense_nearby_ruins(self, radius_squared: int=GameConstants.VISION_RADIUS_SQUARED) -> List[MapLocation]:
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)
        result = []
        for loc in self.game.get_all_locations_within_radius_squared(self.robot.loc, radius_squared):
            if self.game.has_ruin(loc):
                result.append(loc)
        return result

    def sense_map_info(self, loc: MapLocation) -> MapInfo: 
        self.assert_not_none(loc)
        self.assert_can_sense_location(loc)
        return self.game.get_map_info(self.robot.team, loc)

    def sense_nearby_map_infos(self, center: MapLocation=None, radius_squared: int=GameConstants.VISION_RADIUS_SQUARED) -> List[MapInfo]:
        if center is None:
            center = self.robot.loc
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)

        map_info = []
        for loc in self.game.get_all_locations_within_radius_squared(center, radius_squared):
            if self.can_sense_location(loc):
                map_info.append(self.game.get_map_info(self.robot.team, loc))
        return map_info
    
    def get_all_locations_within_radius_squared(self, center: MapLocation, radius_squared: int) -> List[MapLocation]:
        self.assert_not_none(center)
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)
        return [loc for loc in self.game.get_all_locations_within_radius_squared(center, radius_squared) if self.can_sense_location(loc)]
    
    def adjacent_location(self, direction: Direction) -> MapLocation:
        return self.robot.loc.add(direction)
    
    # READINESS FUNCTIONS

    def assert_is_action_ready(self) -> None:
        if self.robot.action_cooldown >= GameConstants.COOLDOWN_LIMIT:
            raise RobotError("Robot action cooldown not yet expired")
        if self.robot.paint == 0 and self.robot.type.is_robot_type():
            raise RobotError("Robot cannot act at 0 paint.")
        
    def is_action_ready(self) -> bool:
        try:
            self.assert_is_action_ready()
            return True
        except RobotError:
            return False
        
    def get_action_cooldown_turns(self) -> int:
        return self.robot.action_cooldown
    
    def assert_is_movement_ready(self) -> None:
        if self.robot.movement_cooldown >= GameConstants.COOLDOWN_LIMIT:
            raise RobotError("Robot movement cooldown not yet expired")
        if self.robot.paint == 0 and self.robot.type.is_robot_type():
            raise RobotError("Robot cannot move at 0 paint.")
        
    def is_movement_ready(self) -> bool:
        try:
            self.assert_is_movement_ready()
            return True
        except RobotError:
            return False
        
    def get_movement_cooldown_turns(self) -> int:
        return self.robot.movement_cooldown
    
    # MOVEMEMENT FUNCTIONS

    def assert_can_move(self, direction: Direction) -> None:
        self.assert_not_none(direction)
        self.assert_is_movement_ready()
        new_location = self.robot.loc.add(direction)
        
        if not self.game.on_the_map(new_location):
            raise RobotError("Robot moved off the map")
        if self.game.get_robot(new_location) is not None:
            raise RobotError("Location is already occupied")
        if not self.game.is_passable(new_location):
            raise RobotError("Trying to move to an impassable location")
        if self.robot.type.is_tower_type():
            raise RobotError("Towers cannot move!")

    def can_move(self, direction: Direction) -> bool:
        try:
            self.assert_can_move(direction)
            return True
        except RobotError:
            return False

    def move(self, direction: Direction) -> None:
        self.assert_can_move(direction)
        self.robot.add_movement_cooldown()
        new_loc = self.robot.loc.add(direction)
        self.game.move_robot(self.robot.loc, new_loc)
        self.robot.loc = new_loc

    # ATTACK FUNCTIONS

    def assert_can_attack(self, loc: MapLocation) -> None:
        """
        Assert that the robot can attack. This function checks all conditions necessary
        for the robot to perform an attack and raises an error if any are not met.
        """
        if loc == None and not self.robot.type in {RobotType.SOLDIER, RobotType.SPLASHER}:
            return
        if not self.game.on_the_map(loc):
            raise RobotError("Outside of Map")
        if self.game.walls[self.game.loc_to_index(loc)]:
            raise RobotError("Outside of Map")
        if self.robot.action_cooldown > self.robot.type.action_cooldown:
            raise RobotError("Action cooldown is in progress.")

        if self.robot.type in {RobotType.SOLDIER, RobotType.SPLASHER, RobotType.MOPPER}:
            if not loc.is_within_distance_squared(self.robot.loc, self.robot.type.action_radius_squared):
                raise RobotError("Target location is out of action range.")
            if self.robot.paint < self.robot.type.attack_cost:
                raise RobotError("Insufficient paint to perform attack.")
                
        elif self.robot.type.is_tower_type():
            if not loc.is_within_distance_squared(self.robot.loc, self.robot.type.action_radius_squared):
                raise RobotError("Target location is out of action range.")
            if loc == None and self.robot.has_tower_area_attacked:
                raise RobotError("Tower cannot use area attack more than once per turn.")
            if loc is not None and self.robot.has_tower_single_attacked:
                raise RobotError("Tower cannot use single tile attack more than once per turn.")

    def can_attack(self, loc: MapLocation) -> bool:
        """
        Check if the robot can attack. This function calls `assert_can_attack`
        and returns a boolean value: True if the attack can proceed, False otherwise.
        """
        try:
            self.assert_can_attack(loc)
            return True
        except RobotError:
            return False

    def attack(self, loc: MapLocation, use_secondary_color: bool=False) -> None:
        self.assert_can_attack(loc)
        self.robot.add_action_cooldown()

        if self.robot.type == RobotType.SOLDIER:
            paint_type = (
                self.game.get_secondary_paint(self.robot.team) 
                if use_secondary_color 
                else self.game.get_primary_paint(self.robot.team)
            )
            self.robot.add_paint(-self.robot.type.attack_cost)

            target_robot = self.game.get_robot(loc)
            if target_robot and target_robot.type.is_tower_type() and target_robot.team != self.robot.team:
                target_robot.add_health(-self.robot.type.attack_strength)
                self.game.game_fb.add_attack_action(target_robot.id)
                self.game.game_fb.add_damage_action(target_robot.id, self.robot.type.attack_strength)
            else:
                self.game.set_paint(loc, paint_type)

        elif self.robot.type == RobotType.SPLASHER:
            paint_type = (
                self.game.get_secondary_paint(self.robot.team) 
                if use_secondary_color 
                else self.game.get_primary_paint(self.robot.team)
            )
            self.robot.add_paint(-self.robot.type.attack_cost)
            
            all_locs = self.game.get_all_locations_within_radius_squared(loc, GameConstants.SPLASHER_ATTACK_AOE_RADIUS_SQUARED)
            for new_loc in all_locs:
                target_robot = self.game.get_robot(new_loc)
                if target_robot and target_robot.type.is_tower_type() and target_robot.team != self.robot.team:
                    target_robot.add_health(-self.robot.type.attack_strength)
                    self.game.game_fb.add_attack_action(target_robot.id)
                    self.game.game_fb.add_damage_action(target_robot.id, self.robot.type.attack_strength)
                else:
                    tile_paint = self.game.get_paint_num(new_loc)
                    if (self.game.team_from_paint(tile_paint) != self.robot.team.opponent or
                            new_loc.is_within_distance_squared(loc, GameConstants.SPLASHER_ATTACK_ENEMY_PAINT_RADIUS_SQUARED)):
                        self.game.set_paint(new_loc, paint_type)

        elif self.robot.type == RobotType.MOPPER:
            if loc is None:
                self.mop_swing() 
            else:
                paint_type = (
                    self.game.get_secondary_paint(self.robot.team) 
                    if use_secondary_color 
                    else self.game.get_primary_paint(self.robot.team)
                )
                self.robot.add_paint(-self.robot.type.attack_cost)
                
                target_robot = self.game.get_robot(loc)
                if target_robot and target_robot.type.is_robot_type() and target_robot.team != self.robot.team:
                    target_robot.add_paint(-GameConstants.MOPPER_ATTACK_PAINT_DEPLETION)
                    self.robot.add_paint(GameConstants.MOPPER_ATTACK_PAINT_ADDITION)
                    self.game.game_fb.add_attack_action(target_robot.id)                    
                
                tile_paint = self.game.get_paint_num(loc)
                if tile_paint != 0 and self.game.team_from_paint(tile_paint) != self.robot.team:
                    self.game.set_paint(loc, 0)

        else:  # Tower
            if loc is None:
                self.robot.has_tower_area_attacked = True
                all_locs = self.game.get_all_locations_within_radius_squared(self.robot.loc, self.robot.type.action_radius_squared)
                for new_loc in all_locs:
                    target_robot = self.game.get_robot(new_loc)
                    if target_robot and target_robot.team != self.robot.team:
                        target_robot.add_health(-self.robot.type.aoe_attack_strength)
                        self.game.game_fb.add_attack_action(target_robot.id)
                        self.game.game_fb.add_damage_action(target_robot.id, self.robot.type.aoe_attack_strength)
            else:
                self.robot.has_tower_single_attacked = True
                target_robot = self.game.get_robot(loc)
                if target_robot and target_robot.team != self.robot.team:
                    target_robot.add_health(-self.robot.type.attack_strength)
                    self.game.game_fb.add_attack_action(target_robot.id)
                    self.game.game_fb.add_damage_action(target_robot.id, self.robot.type.attack_strength)

    def assert_can_mop_swing(self, dir: Direction) -> None:
        self.assert_not_none(dir)
        self.assert_is_action_ready()
        if not dir in {Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST}:
            raise RobotError("Must pass in a cardinal direction to mop swing")
        if self.robot.type != RobotType.MOPPER:
            raise RobotError("Unit must be a mopper!")
        next_loc = self.robot.loc.add(dir)
        if not self.on_the_map(next_loc):
            raise RobotError("Can't do a mop swing off the edge of the map!")

    def can_mop_swing(self, dir: Direction) -> bool:
        try:
            self.assert_can_mop_swing(dir)
            return True
        except RobotError:
            return False

    def mop_swing(self, dir: Direction) -> None:
        self.assert_can_mop_swing()

        swing_offsets = {
            Direction.NORTH: ((-1, 1), (0, 1), (1, 1)),
            Direction.SOUTH: ((-1, -1), (0, -1), (1, -1)),
            Direction.EAST: ((1, -1), (1, 0), (1, 1)),
            Direction.WEST: ((-1, -1), (-1, 0), (-1, 1))
        }

        target_ids = []
        for i in range(3):
            offset = swing_offsets[dir][i]
            new_loc = MapLocation(self.robot.loc.x + offset[0], self.robot.loc.y + offset[1])
            target_robot = self.game.get_robot(new_loc)
            if target_robot and target_robot.team != self.robot.team:
                target_robot.add_paint(-GameConstants.MOPPER_SWING_PAINT_DEPLETION)
                target_ids.append(target_robot.id)
            target_ids.append(0)
        self.game.game_fb.add_mop_action(target_ids[0], target_ids[1], target_ids[2])

    # MARKING FUNCTIONS

    def assert_can_mark_pattern(self, loc: MapLocation) -> None:
        '''
        Asserts that a pattern can be marked at this location.
        '''
        if self.robot.type.is_tower_type():
            raise RobotError("Marking unit is not a robot.")
        if self.game.is_valid_pattern_center(loc):
            raise RobotError(f"Pattern at ({loc.x}, {loc.y}) is out of the bounds of the map.")
        if not loc.is_within_distance_squared(self.robot.loc, GameConstants.MARK_RADIUS_SQUARED):
            raise RobotError(f"({loc.x}, {loc.y}) is not within the robot's pattern-marking range")
        if self.robot.paint < GameConstants.MARK_PATTERN_COST:
            raise RobotError("Robot does not have enough paint for mark the pattern.")
        
    def assert_can_mark_tower_pattern(self, loc: MapLocation, tower_type: RobotType) -> None:
        '''
        Asserts that tower pattern can be marked at this location.
        '''
        self.assert_can_mark_pattern(loc)
        if tower_type.is_robot_type():
            raise RobotError("Pattern type is not a tower type.")
        if not self.game.get_map_info(self.robot.team, loc).has_ruin():
            raise RobotError(f"Cannot mark tower pattern at ({loc.x}, {loc.y}) because there is no ruin.")
        
    def assert_can_mark_resource_pattern(self, loc: MapLocation) -> None:
        '''
        Asserts that tower pattern can be marked at this location.
        '''
        self.assert_can_mark_pattern(loc)

    def can_mark_tower_pattern(self, loc: MapLocation, tower_type: RobotType) -> bool:
        """
        Checks if specified tower pattern can be marked at location
        """
        try:
            self.assert_can_mark_tower_pattern(loc, tower_type)
            return True
        except:
            return False
        
    def can_mark_resource_pattern(self, loc: MapLocation) -> bool:
        """
        Checks if resource pattern can be marked at location
        """
        try:
            self.assert_can_mark_resource_pattern(loc)
            return True
        except:
            return False
        
    def mark_tower_pattern(self, loc: MapLocation, tower_type: RobotType) -> None:
        """
        Marks specified tower pattern at location if possible
        tower_type: RobotType enum
        """
        self.assert_can_mark_tower_pattern(loc, tower_type)
        self.robot.add_paint(-GameConstants.MARK_PATTERN_COST)
        self.game.mark_tower_pattern(self.robot.team, loc, tower_type) #TODO: implement mark_tower_pattern in game.py

    def mark_resource_pattern(self, loc: MapLocation) -> None:
        """
        Marks resource pattern at location if possible
        """
        self.assert_can_mark_resource_pattern(loc)
        self.robot.add_paint(-GameConstants.MARK_PATTERN_COST)
        self.game.mark_resource_pattern(self.robot.team, loc) #TODO: implement mark_resource_pattern in game.py 

    def assert_can_mark(self, loc: MapLocation) -> None:
        self.assert_is_robot_type(self.robot.type)
        self.assert_can_act_location(loc, GameConstants.MARK_RADIUS_SQUARED)

    def can_mark(self, loc: MapLocation) -> bool:
        """
        Checks if the robot can mark a location.
        Returns True if marking conditions are met, otherwise False
        """
        try:
            self.assert_can_mark(loc)
            return True
        except RobotError:
            return False

    def mark(self, loc: MapLocation, secondary: bool) -> None:
        """
        Marks the specified map location
        loc: MapLocation we want to mark
        color: Color enum specifying the color of the mark
        """
        self.assert_can_mark(loc)
        self.game.mark_location(self.robot.team, loc, secondary)
        self.game.game_fb.add_mark_action(loc, secondary)

    def assert_can_remove_mark(self, loc: MapLocation) -> None:
        self.assert_is_robot_type(self.robot.type)
        self.assert_can_act_location(loc, GameConstants.MARK_RADIUS_SQUARED)

        if self.game.get_marker(loc) == 0:
            raise RobotError("Cannot remove mark from unmarked location")

    def can_remove_mark(self, loc: MapLocation) -> bool: 
        try:
            self.assert_can_remove_mark(loc)
            return True
        except RobotError:
            return False

    def remove_mark(self, loc: MapLocation) -> None:
        self.assert_can_remove_mark(loc)
        self.game.mark_location(self.robot.team, loc, 0) 
        self.game.game_fb.add_unmark_action(loc)
    
    def assert_can_complete_tower_pattern(self, loc: MapLocation, tower_type: RobotType) -> None:
        self.assert_is_robot_type(self.robot.type)
        self.assert_is_tower_type(tower_type)
        self.assert_can_act_location(loc, GameConstants.BUILD_TOWER_RADIUS_SQUARED)

        if self.game.has_tower(loc):
            raise RobotError(f"Cannot complete tower pattern at ({loc.x}, {loc.y}) because the center already contains a tower")
        if not self.game.has_ruin(loc):
            raise RobotError(f"Cannot complete tower pattern at ({loc.x}, {loc.y}) because the center is not a ruin")
        if not self.game.is_valid_pattern_center(loc):
            raise RobotError(f"Cannot complete tower pattern at ({loc.x}, {loc.y}) because it is too close to the edge of the map")
        if self.game.get_robot(loc) is not None:
            raise RobotError(f"Cannot complete tower pattern at ({loc.x}, {loc.y}) because there is a robot at the center of the ruin")
        if not self.game.detect_pattern(loc, self.robot.team) == tower_type:
            raise RobotError(f"Cannot complete tower pattern at ({loc.x}, {loc.y}) because the paint pattern is wrong")
        
    def can_complete_tower_pattern(self, loc: MapLocation, tower_type: RobotType, ) -> bool:
        try:
            self.assert_can_complete_tower_pattern(loc, tower_type)
            return True
        except RobotError:
            return False
        
    def complete_tower_pattern(self, loc: MapLocation, tower_type: RobotType) -> None:
        self.assert_can_complete_tower_pattern(loc, tower_type)
        robot = self.game.spawn_robot(tower_type, loc, self.robot.team)
        self.game.game_fb.add_build_action(robot.id)

    def assert_can_complete_resource_pattern(self, loc: MapLocation) -> None:
        self.assert_is_robot_type(self.robot.type)
        self.assert_can_act_location(loc, GameConstants.RESOURCE_PATTERN_RADIUS_SQUARED)

        if not self.game.is_valid_pattern_center(loc):
            raise RobotError(f"Cannot complete resource pattern at ({loc.x}, {loc.y}) because it is too close to the edge of the map")
        if not self.game.detect_pattern(loc, self.robot.team) == Shape.RESOURCE:
            raise RobotError(f"Cannot complete resource pattern at ({loc.x}, {loc.y}) because the paint pattern is wrong")
        
    def can_complete_resource_pattern(self, loc: MapLocation) -> bool:
        try:
            self.assert_can_complete_resource_pattern(loc)
            return True
        except RobotError:
            return False
        
    def complete_resource_pattern(self, loc: MapLocation) -> None:
        self.assert_can_complete_resource_pattern(loc)
        self.game.complete_resource_pattern(self.robot.team, loc)
           
    # BUILDING FUNCTIONS

    def assert_can_build_robot(self, robot_type: RobotType, map_location: MapLocation) -> None:
        self.assert_not_none(robot_type)
        self.assert_not_none(map_location)
        self.assert_can_act_location(map_location, GameConstants.BUILD_ROBOT_RADIUS_SQUARED)
        self.assert_is_action_ready()
        self.assert_is_tower_type(self.robot.type)
        self.assert_is_robot_type(robot_type)

        if self.robot.paint < robot_type.paint_cost:
            raise RobotError("Insufficient resources: Not enough paint to spawn robot")
        if self.game.team_info.get_coins(self.robot.team) < robot_type.money_cost:
            raise RobotError("Insufficient resources: Not enough money to spawn robot")
        if self.game.get_robot(map_location) is not None:
            raise RobotError("Build location is already occupied.")
        if not self.game.is_passable(map_location):
            raise RobotError("Build location is has a wall.")
        
    def can_build_robot(self, robot_type: RobotType, map_location: MapLocation) -> bool:
        """
        Checks if the specified robot can spawn a new unit.
        Returns True if spawning conditions are met, otherwise False.
        """
        try:
            self.assert_can_build_robot(robot_type, map_location)
            return True
        except RobotError as e:
            return False

    def build_robot(self, robot_type: RobotType, map_location: MapLocation) -> None:
        """
        Spawns a new robot of the given type at a specific map location if conditions are met.
        """
        self.assert_can_build_robot(robot_type, map_location)
        robot = self.game.spawn_robot(robot_type, map_location, self.robot.team)
        self.robot.add_action_cooldown()
        self.robot.add_paint(-robot_type.paint_cost)
        self.game.team_info.add_coins(self.robot.team, -robot_type.money_cost)
        self.game.game_fb.add_spawn_action(robot.id, robot.loc, robot.team, robot.type)

    # COMMUNICATION FUNCTIONS

    def assert_can_send_message(self, loc: MapLocation) -> None:
        self.assert_not_none(loc)
        self.assert_can_act_location(loc, GameConstants.MESSAGE_RADIUS_SQUARED)
        target = self.game.get_robot(loc)
        self.assert_not_none(target)
        if target.team != self.robot.team:
            raise RobotError("Cannot send messages to robots of the enemy team!")
        if self.robot.type.is_robot_type() == target.type.is_robot_type():
            raise RobotError("Only (robot <-> tower) communication is allowed!")
        if self.robot.type.is_robot_type():
            if self.robot.sent_message_count >= GameConstants.MAX_MESSAGES_SENT_ROBOT:
                raise RobotError("Robot has already sent too many messages this round!")
        elif self.robot.sent_message_count >= GameConstants.MAX_MESSAGES_SENT_TOWER:
            raise RobotError("Tower has already sent too many messages this round!")
        if not self.game.connected_by_paint(self.robot.loc, target.loc):
            raise RobotError("Location specified is not connected to current location by paint!")

    def can_send_message(self, loc: MapLocation) -> bool:
        try:
            self.assert_can_send_message(loc)
            return True
        except RobotError as e:
            return False

    def send_message(self, loc: MapLocation, message_content: int) -> None:
        self.assert_can_send_message(loc)
        target = self.game.get_robot(loc)
        target.message_buffer.add_message(message_content)
        self.robot.sent_message_count += 1
        self.game.game_fb.add_message_action(target.id, message_content)

    def read_messages(self, round=-1) -> List[int]:
        if round == -1:
            return self.robot.message_buffer.get_all_messages()
        return self.robot.message_buffer.get_messages(round)

    # TRANSFER PAINT FUNCTIONS

    def assert_can_transfer_paint(self, loc: MapLocation, amount: int) -> None:
        self.assert_not_none(loc)
        self.assert_can_act_location(loc, GameConstants.PAINT_TRANSFER_RADIUS_SQUARED)
        target = self.game.get_robot(loc)
        self.assert_not_none(target)
        self.assert_is_action_ready()

        if loc == self.robot.loc:
            raise RobotError("Cannot transfer paint to yourself!")
        if amount == 0:
            raise RobotError("Cannot transfer zero paint!")
        if target.team != self.robot.team:
            raise RobotError("Cannot transfer resources to the enemy team!")
        if self.robot.type.is_tower_type():
            raise RobotError("Towers cannot transfer paint!")        
        if amount > 0: #positive give paint, negative take paint
            if self.robot.type != RobotType.MOPPER:
                raise RobotError("Only moppers can give paint to allies!")
            if amount > self.robot.paint:
                raise RobotError("Cannot give more paint than you currently have!")
        else:
            if target.type.is_robot_type():
                raise RobotError("Paint can be taken only from towers")
            if -amount > target.paint:
                raise RobotError("Cannot take more paint from towers than they currently have!")

    def can_transfer_paint(self, target_location: MapLocation, amount: int) -> bool:
        try:
            self.assert_can_transfer_paint(target_location, amount)
            return True
        except RobotError as e:
            return False

    def transfer_paint(self, target_location: MapLocation, amount: int) -> None:
        self.assert_can_transfer_paint(target_location, amount)
        self.robot.add_paint(-amount)
        target = self.game.get_robot(target_location)
        target.add_paint(amount)
        self.robot.add_action_cooldown()
        self.game.game_fb.add_transfer_action(target.id, amount)

    # UPGRADE TOWER FUNCTIONS

    def assert_can_upgrade_tower(self, loc: MapLocation) -> None: 
        self.assert_not_none(loc)
        self.assert_can_act_location(loc, GameConstants.BUILD_TOWER_RADIUS_SQUARED)

        tower = self.game.get_robot(loc)
        self.assert_not_none(tower)
        if not tower.type.is_tower_type(): 
            raise RobotError("Cannot upgrade a robot that is not a tower.")
        if tower.team != self.robot.team: 
            raise RobotError("Cannot upgrade opposing team's towers.")
        if tower.type.level == 3: 
            raise RobotError("Cannot upgrade anymore, tower is already at the maximum level.")
        new_type = self.robot.type.get_next_level()
        if self.game.team_info.get_coins(self.robot.team) < new_type.money_cost: 
            raise RobotError("Not enough coins to upgrade the tower.")

    def can_upgrade_tower(self, tower_location: MapLocation) -> bool: 
        try: 
            self.assert_can_upgrade_tower(tower_location)
            return True
        except RobotError as e: 
            return False

    def upgrade_tower(self, tower_location: MapLocation) -> None: 
        self.assert_can_upgrade_tower(tower_location)
        tower = self.game.get_robot(tower_location)
        new_type = tower.type.get_next_level()
        self.game.team_info.add_coins(self.robot.team, -new_type.money_cost)
        tower.upgrade_tower()
        self.game.game_fb.add_upgrade_action(tower.id)

    # DEBUG INDICATOR FUNCTIONS

    def set_indicator_string(self, string: str) -> None:
        if len(string) > GameConstants.INDICATOR_STRING_MAX_LENGTH:
            string = string[:GameConstants.INDICATOR_STRING_MAX_LENGTH]
        self.robot.indicator_string = string

    def set_indicator_dot(self, loc: MapLocation, red: int, green: int, blue: int) -> None:
        self.assert_not_none(loc)
        self.game.game_fb.add_indicator_dot(loc, red, green, blue)

    def set_indicator_line(self, start_loc: MapLocation, end_loc: MapLocation, red: int, green: int, blue: int) -> None:
        self.assert_not_none(start_loc)
        self.assert_not_none(end_loc)
        self.game.game_fb.add_indicator_line(start_loc, end_loc, red, green, blue)

    def set_timeline_marker(self, label: str, red: int, green: int, blue: int) -> None:
        if len(label) > GameConstants.INDICATOR_STRING_MAX_LENGTH:
            label = label[:GameConstants.INDICATOR_STRING_MAX_LENGTH]
        self.game.game_fb.add_timeline_marker(self.robot.team, label, red, green, blue)

    def resign(self) -> None:
        self.game.set_winner(self.robot.team.opponent(), DominationFactor.RESIGNATION)
    
class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass