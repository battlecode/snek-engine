from __future__ import annotations
import random
from .map_info import MapInfo
from .robot import Robot
from .team import Team
from .robot_type import RobotType
from .constants import GameConstants
from .map_location import MapLocation
from .robot_info import RobotInfo
from .direction import Direction
from .shape import Shape

#Imported for type checking
if 1 == 0:
    from .game import Game

#### SHARED METHODS ####

class RobotController:

    def __init__(self, game: Game, robot: Robot):
        self.game = game
        self.robot = robot

    # INTERNAL HELPERS

    def assert_not_none(self, o):
        if o is None:
            raise RobotError("Argument has invalid None value")

    def assert_can_act_location(self, loc, max_radius_squared):
        self.assert_not_none(loc)
        if self.robot.loc.distance_squared_to(loc) > max_radius_squared:
            raise RobotError("Target location is not within action range")
        if not self.game.on_the_map(loc):
            raise RobotError("Target location is not on the map")
        
    def assert_is_robot_type(self, type: RobotType):
        if not type.is_robot_type():
            raise RobotError("Towers cannot perform this action")
        
    def assert_is_tower_type(self, type: RobotType):
        if not type.is_tower_type():
            raise RobotError("Robots cannot perform this action")

    # GLOBAL QUERY FUNCTIONS

    def get_round_num(self):
        return self.game.round

    def get_map_width(self):
        return self.game.width

    def get_map_height(self):
        return self.game.height
    
    def get_resource_pattern(self):
        return self.game.pattern[Shape.RESOURCE.value]
    
    def get_tower_pattern(self, tower_type):
        self.assert_is_tower_type(tower_type)
        return self.game.pattern[self.game.shape_from_tower_type(tower_type).value]
    
    # ROBOT QUERY FUNCTIONS

    def get_id(self):
        return self.robot.id

    def get_team(self):
        """
        Return the current robot's team (Team.A or Team.B)
        """
        return self.robot.team
    
    def get_paint(self):
        return self.robot.paint
    
    def get_location(self):
        return self.robot.loc
    
    def get_health(self):
        return self.robot.health
    
    def get_money(self):
        return self.game.team_info.get_coins(self.robot.team)

    def get_type(self):
        return self.robot.type

    # SENSING FUNCTIONS

    def on_the_map(self, loc):
        self.assert_not_none(loc)
        return self.game.on_the_map(loc)

    def assert_can_sense_location(self, loc):
        self.assert_not_none(loc)
        if not self.game.on_the_map(loc):
            raise RobotError("Target location is not on the map")
        if self.robot.loc.distance_squared_to(loc) > GameConstants.VISION_RADIUS_SQUARED:
            raise RobotError("Target location is out of vision range")

    def can_sense_location(self, loc):
        try:
            self.assert_can_sense_location(loc)
            return True
        except RobotError:
            return False

    def is_location_occupied(self, loc):
        self.assert_can_sense_location(loc)
        return self.game.get_robot(loc) is not None

    def can_sense_robot_at_location(self, loc):
        try:
            return self.is_location_occupied(loc)
        except RobotError:
            return False

    def sense_robot_at_location(self, loc):
        self.assert_can_sense_location(loc)
        robot = self.game.get_robot(loc)
        return None if robot is None else robot.get_robot_info()   

    def can_sense_robot(self, robot_id):
        sensed_robot = self.game.get_robot_by_id(robot_id)
        return sensed_robot is not None and self.can_sense_location(sensed_robot.loc)

    def sense_robot(self, robot_id):
        if not self.can_sense_robot(robot_id):
            raise RobotError("Cannot sense robot; It may be out of vision range not exist")
        return self.game.get_robot_by_id(robot_id).get_robot_info()
    
    def assert_radius_non_negative(self, radius):
        if radius < 0:
            raise RobotError("Radius is negative")

    def sense_nearby_robots(self, center=None, radius_squared=GameConstants.VISION_RADIUS_SQUARED, team=None):
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
    
    def sense_passability(self, loc):
        self.assert_can_sense_location(loc)
        return self.game.is_passable(loc)
    
    def sense_nearby_ruins(self, radius_squared=GameConstants.VISION_RADIUS_SQUARED):
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)
        result = []
        for loc in self.game.get_all_locations_within_radius_squared(self.robot.loc, radius_squared):
            if self.game.has_ruin(loc):
                result.append(loc)
        return result

    def sense_map_info(self, loc): 
        self.assert_not_none(loc)
        self.assert_can_sense_location(loc)
        return self.game.get_map_info(loc)

    def sense_nearby_map_info(self, center=None, radius_squared=GameConstants.VISION_RADIUS_SQUARED):
        if center is None:
            center = self.robot.loc
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)

        map_info = []
        for loc in self.game.get_all_locations_within_radius_squared(center, radius_squared):
            if self.can_sense_location(loc):
                map_info.append(self.game.get_map_info(loc))
        return map_info
    
    def get_all_locations_within_radius_squared(self, center, radius_squared):
        self.assert_not_none(center)
        self.assert_radius_non_negative(radius_squared)
        radius_squared = min(radius_squared, GameConstants.VISION_RADIUS_SQUARED)
        return [loc for loc in self.game.get_all_locations_within_radius_squared(center, radius_squared) if self.can_sense_location(loc)]
    
    def adjacent_location(self, direction):
        return self.robot.loc.add(direction)
    
    #### MOVEMENT METHODS ####
    def assert_can_move(self, direction):
        if direction is None:
            raise RobotError("Not a valid direction")
        if self.robot.movement_cooldown >= GameConstants.COOLDOWN_LIMIT:
            raise RobotError("Robot movement cooldown not yet expired")

        new_location = self.robot.loc.add(direction)
        if not self.game.on_the_map(new_location):
            raise RobotError("Robot moved off the map")
        if self.game.robots[self.game.loc_to_index(new_location)] is not None:
            raise RobotError("Location is already occupied")
        if not self.game.is_passable(new_location):
            raise RobotError("Trying to move to an impassable location")

    def can_move(self, direction):
        try:
            self.assert_can_move(direction)
            return True
        except RobotError:
            return False

    def move(self, direction):
        self.assert_can_move(direction)
        self.robot.add_movement_cooldown()
        new_loc = self.robot.loc.add(direction)
        self.game.move_robot(self.robot.loc, new_loc)
        self.robot.loc = new_loc

    #### ATTACK METHODS ####
    def assert_can_attack(self, loc):
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

    def can_attack(self, loc):
        """
        Check if the robot can attack. This function calls `assert_can_attack`
        and returns a boolean value: True if the attack can proceed, False otherwise.
        """
        try:
            self.assert_can_attack(loc)
            return True
        except RobotError:
            return False

    def attack(self, loc, use_secondary_color=False):
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
                self.game.game_fb.add_paint_action(loc, use_secondary_color)

        elif self.robot.type == RobotType.SPLASHER:
            paint_type = (
                self.game.get_secondary_paint(self.robot.team) 
                if use_secondary_color 
                else self.game.get_primary_paint(self.robot.team)
            )
            self.robot.add_paint(-self.robot.type.attack_cost)

            all_locs = self.game.get_all_locations_within_radius_squared(loc, 2)
            for new_loc in all_locs:
                if not self.can_attack(loc):
                    continue
                target_robot = self.game.get_robot(new_loc)
                if target_robot and target_robot.type.is_tower_type() and target_robot.team != self.robot.team:
                    target_robot.add_health(-self.robot.type.attack_strength)
                    self.game.game_fb.add_attack_action(target_robot.id)
                    self.game.game_fb.add_damage_action(target_robot.id, self.robot.type.attack_strength)
                else:
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
                    self.game.game_fb.add_mop_action(loc)
                    

                else:
                    self.game.set_paint(loc, 0)

        else:  # Tower
            if loc is None:
                self.robot.has_tower_area_attacked = True
                all_locs = self.game.get_all_locations_within_radius_squared(self.robot.loc, self.robot.type.action_radius_squared)
                for new_loc in all_locs:
                    if not self.can_attack(loc):
                        continue
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

    def mop_swing(self):
        assert self.robot.type == RobotType.MOPPER, "mop_swing called on non-MOPPER robot"
        # Example direction; you might want to pass direction as a parameter
        directions = [Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST]
        for direction in directions:
            dx = dy = 0  # Define based on direction
            if direction == Direction.SOUTH:
                dx, dy = 1, 0
            elif direction == Direction.EAST:
                dx, dy = 0, 1
            elif direction == Direction.WEST:
                dx, dy = 0, -1
            elif direction == Direction.NORTH:
                dx, dy = -1, 0

            x = self.robot.loc.x + dx
            y = self.robot.loc.y + dy
            new_loc = MapLocation(x, y)
        
            if not self.can_attack(new_loc):
                continue
        
            target_robot = self.game.get_robot(new_loc)
            if target_robot and target_robot.team != self.robot.team:
                target_robot.add_paint(-GameConstants.MOPPER_SWING_PAINT_DEPLETION)
                self.game.game_fb.add_attack_action(target_robot.id)
                self.game.game_fb.add_mop_action(new_loc)

    # MARKING METHODS
    def assert_can_mark_pattern(self, loc):
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
        
    def assert_can_mark_tower_pattern(self, loc, tower_type):
        '''
        Asserts that tower pattern can be marked at this location.
        '''
        self.assert_can_mark_pattern(loc)
        if tower_type.is_robot_type():
            raise RobotError("Pattern type is not a tower type.")
        if not self.game.get_map_info(loc).has_ruin():
            raise RobotError(f"Cannot mark tower pattern at ({loc.x}, {loc.y}) because there is no ruin.")
        
    def assert_can_mark_resource_pattern(self, loc):
        '''
        Asserts that tower pattern can be marked at this location.
        '''
        self.assert_can_mark_pattern(loc)

    def can_mark_tower_pattern(self, loc, tower_type):
        """
        Checks if specified tower pattern can be marked at location
        """
        try:
            self.assert_can_mark_tower_pattern(loc, tower_type)
            return True
        except:
            return False
        
    def can_mark_resource_pattern(self, loc):
        """
        Checks if resource pattern can be marked at location
        """
        try:
            self.assert_can_mark_resource_pattern(loc)
            return True
        except:
            return False
        
    def mark_tower_pattern(self, loc, tower_type):
        """
        Marks specified tower pattern at location if possible
        tower_type: RobotType enum
        """
        self.assert_can_mark_tower_pattern(loc)
        self.robot.add_paint(-GameConstants.MARK_PATTERN_COST)
        self.game.mark_tower_pattern(self.robot.team, loc, tower_type) #TODO: implement mark_tower_pattern in game.py

    def mark_resource_pattern(self, loc):
        """
        Marks resource pattern at location if possible
        """
        self.assert_can_mark_resource_pattern(loc)
        self.robot.add_paint(-GameConstants.MARK_PATTERN_COST)
        self.game.mark_resource_pattern(self.robot.team, loc) #TODO: implement mark_resource_pattern in game.py 

    def assert_can_mark(self, loc):
        self.assert_is_robot_type(self.robot.type)
        self.assert_can_act_location(loc, GameConstants.MARK_RADIUS_SQUARED)

    def can_mark(self, loc):
        """
        Checks if the robot can mark a location.
        Returns True if marking conditions are met, otherwise False
        """
        try:
            self.assert_can_mark(loc)
            return True
        except RobotError:
            return False

    def mark(self, loc, secondary: bool):
        """
        Marks the specified map location
        loc: MapLocation we want to mark
        color: Color enum specifying the color of the mark
        """
        self.assert_can_mark(loc)
        color = self.game.get_primary_paint(self.robot.team) if not secondary else self.game.get_secondary_paint(self.robot.team)
        self.game.mark_location(self.robot.team, loc, color)
    
    def assert_can_complete_tower_pattern(self, tower_type, loc):
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
        
    def can_complete_tower_pattern(self, tower_type, loc):
        try:
            self.assert_can_complete_tower_pattern(tower_type, loc)
            return True
        except RobotError:
            return False
        
    def complete_tower_pattern(self, tower_type, loc):
        self.assert_can_complete_tower_pattern(tower_type, loc)
        robot = self.game.spawn_robot(tower_type, loc, self.robot.team)
        self.game.game_fb.add_build_action(robot.id)

    def assert_can_complete_resource_pattern(self, loc):
        self.assert_is_robot_type(self.robot.type)
        self.assert_can_act_location(loc, GameConstants.RESOURCE_PATTERN_RADIUS_SQUARED)

        if not self.game.is_valid_pattern_center(loc):
            raise RobotError(f"Cannot complete resource pattern at ({loc.x}, {loc.y}) because it is too close to the edge of the map")
        if not self.game.detect_pattern(loc, self.robot.team) == Shape.RESOURCE:
            raise RobotError(f"Cannot complete resource pattern at ({loc.x}, {loc.y}) because the paint pattern is wrong")
        
    def can_complete_resource_pattern(self, loc):
        try:
            self.assert_can_complete_resource_pattern(loc)
            return True
        except RobotError:
            return False
        
    def complete_resource_pattern(self, loc):
        self.assert_can_complete_resource_pattern(loc)
        self.game.complete_resource_pattern(self.robot.team, loc)
           
    #### SPAWN METHODS ####
    def assert_spawn(self, robot_type, map_location):
        """
        Assert that the specified robot can spawn a new unit. Raises RobotError if it can't.
        """
        if not self.on_the_map(map_location):
            raise RobotError("Build location is out of bounds.")
        if not self.robot.type.is_tower_type() and self.robot.action_cooldown > self.robot.type.action_cooldown:
            raise RobotError("Robot cannot spawn: it must be a tower and its action cooldown must be ready.")
        
        if self.robot.paint < robot_type.paint_cost or self.game.team_info.get_coins(self.robot.team) < robot_type.money_cost:
            raise RobotError("Insufficient resources: Not enough paint or money to spawn this robot.")
        
        if not self.robot.loc.is_within_distance_squared(map_location, 3):
            raise RobotError("Target location is out of the tower's spawn radius.")
        if self.game.robots:
            if self.game.get_robot(map_location):
                raise RobotError("Build location is already occupied.")
        

    def can_spawn(self, robot_type, map_location):
        """
        Checks if the specified robot can spawn a new unit.
        Returns True if spawning conditions are met, otherwise False.
        """
        try:
            self.assert_spawn(robot_type, map_location)
            return True
        except RobotError as e:
            return False

    def spawn(self, robot_type, map_location):
        """
        Spawns a new robot of the given type at a specific map location if conditions are met.
        """
        self.assert_spawn(robot_type, map_location)
        robot = self.game.spawn_robot(robot_type, map_location, self.robot.team)
        self.robot.add_action_cooldown()  # Adjust cooldown as needed
        self.robot.add_paint(-robot_type.paint_cost)
        self.game.team_info.add_coins(self.robot.team, -robot_type.money_cost)
        self.game.game_fb.add_spawn_action(robot.id, robot.loc, robot.team, robot.type)
        print("----------------------SPAWNED")

    #### MESSAGE METHODS ####
    def assert_can_send_message(self, loc):
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

    def can_send_message(self, loc):
        try:
            self.assert_can_send_message(loc)
            return True
        except RobotError as e:
            return False

    def send_message(self, loc, message_content):
        self.assert_can_send_message(loc)
        target = self.game.get_robot(loc)
        target.message_buffer.add_message(message_content)
        self.robot.sent_message_count += 1
        self.game.game_fb.add_message_action(target.id, message_content)

    def read_messages(self, round=-1):
        if round == -1:
            return self.robot.message_buffer.get_all_messages()
        return self.robot.message_buffer.get_messages(round)

    #### TRANSFERRING METHODS ####
    def assert_can_transfer_paint(self, target_location, amount):
        if not self.robot.is_action_ready():
            raise RobotError("Robot cannot transfer paint yet; action cooldown in progress.")
        
        if not self.game.is_on_board(target_location.x, target_location.y):
            raise RobotError("Target location is not on the map.")
        
        if self.robot.type != RobotType.MOPPER: 
            raise RobotError("Robot type is not a Mopper, cannot transfer paint.")
        
        distance_squared = self.robot.loc.distanceSquaredTo(target_location)
        if distance_squared > self.robot.type.action_radius_squared:
            raise RobotError(f"Target is out of range for {self.robot.type.name}.")
    
        target = self.game.get_robot(target_location)
        if target is None: 
            raise RobotError(f"There is no robot at {target_location}.")
        if target.team != self.robot.team:
            raise RobotError("Moppers can only transfer paint within their own team")
        
        if amount < 0 and target.paint < -amount: 
            raise RobotError(f"Target does not have enough paint. Tried to request {-amount}, but target only has {target.paint}")
        if amount > 0 and self.robot.paint < amount: 
            raise RobotError("Mopper does not have enough paint to transfer.")

    def can_transfer_paint(self, target_location, amount):
        try:
            self.assert_can_transfer_paint(target_location, amount)
            return True
        except RobotError as e:
            return False

    def transfer_paint(self, target_location, amount):
        self.assert_can_transfer_paint(target_location, amount)
        self.robot.add_paint(-amount)
        target = self.game.get_robot(target_location)
        target.add_paint(amount)

    #### WITHDRAWING METHODS ####
    def assert_can_withdraw_paint(self, target_location, amount): 
        if not self.robot.is_action_ready():
            raise RobotError("Robot cannot withdraw paint yet; action cooldown in progress.")
        
        if not self.game.is_on_board(target_location.x, target_location.y):
            raise RobotError("Target location is not on the map.")
            
        if self.robot.type != RobotType.MOPPER: 
            raise RobotError("Robot type is not a Mopper, cannot withdraw paint.")
        
        distance_squared = self.robot.loc.distanceSquaredTo(target_location)
        if distance_squared > self.robot.type.action_radius_squared:
            raise RobotError(f"Target is out of range for {self.robot.type.name}.")
        
        target = self.game.get_robot(target_location)
        if target is None: 
            raise RobotError(f"There is no robot at {target_location}.")
        if target.team != self.robot.team:
            raise RobotError("Moppers can only withdraw paint within their own team")
        if not target.type.isTower():
            raise RobotError("The object at the target location is not a tower.")

        if amount < 0 and target.paint < -amount: 
            raise RobotError(f"Target does not have enough paint. Tried to request {-amount}, but target only has {target.paint}")
        if amount > 0 and self.robot.paint < amount: 
            raise RobotError("Mopper does not have enough paint to withdraw.")

    def can_withdraw_paint(self, target_location, amount):
        try:
            self.assert_can_withdraw_paint(target_location, amount)
            return True
        except RobotError as e:
            print(f"Withdrawing failed: {e}")
            return False

    def withdraw_paint(self, target_location, amount):
        self.assert_can_withdraw_paint(target_location, amount)
        self.robot.add_paint(amount)
        target = self.game.get_robot(target_location)
        target.add_paint(-amount)

    #### UPGRADING TOWER METHODS ####
    def assert_can_upgrade_tower(self, tower_location): 
        if not self.game.is_on_board(tower_location.x, tower_location.y):
            raise RobotError("Target location is not on the map.")

        tower = self.game.get_robot(tower_location)
        if not tower.type.isTower(): 
            raise RobotError("Cannot upgrade a robot that is not a tower.")
        
        if tower.team != self.robot.team: 
            raise RobotError("Cannot upgrade opposing team's towers.")
        
        if tower.type.level == 3: 
            raise RobotError("Cannot upgrade anymore, tower is already at the maximum level.")
        
        if self.game.teamInfo.get_coins(self.robot.team) < tower.type.money_cost: 
            raise RobotError("Not enough coins to upgrade the tower.")

    def can_upgrade_tower(self, tower_location): 
        try: 
            self.assert_can_upgrade_tower(tower_location)
            return True
        except RobotError as e: 
            print(f"Upgrading failed: {e}")
            return False

    def upgrade_tower(self, tower_location): 
        self.assert_can_upgrade_tower(tower_location)
        tower = self.game.get_robot(tower_location)
        self.game.team_info.add_coins(self.robot.team, -tower.type.money_cost)
        tower.type.upgradeTower(tower)
    
class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass