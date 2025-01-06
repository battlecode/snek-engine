import random
from enum import Enum
from .robot import Robot
from .team import Team
from .unit_type import UnitType
from .constants import GameConstants
from .robot_controller import *
from .map_location import MapLocation
from .team_info import TeamInfo
from .direction import Direction
from .id_generator import IDGenerator
from .initial_map import InitialMap
from .game_fb import GameFB
from .robot_controller import RobotController
from .domination_factor import DominationFactor
from .shape import Shape
from .map_info import MapInfo
from .paint_type import PaintType
from typing import Generator
from .message import Message

import math

class Game:

    def __init__(self, code, initial_map: InitialMap, game_fb: GameFB, game_args):
        random.seed(GameConstants.GAME_DEFAULT_SEED)
        self.width = initial_map.width
        self.height = initial_map.height
        total_area = self.width * self.height
        self.area_without_walls = total_area - sum(initial_map.walls) - sum(initial_map.ruins)
        self.walls = initial_map.walls
        self.ruins = initial_map.ruins
        self.team_a_markers = [0] * total_area
        self.team_b_markers = [0] * total_area
        self.round = 0
        self.id_generator = IDGenerator()
        self.winner = None
        self.domination_factor = None
        self.initial_map = initial_map
        self.team_info = TeamInfo(self)
        self.team_info.add_coins(Team.A, GameConstants.INITIAL_TEAM_MONEY)
        self.team_info.add_coins(Team.B, GameConstants.INITIAL_TEAM_MONEY)
        self.paint = [0] * total_area
        for idx, paint_val in enumerate(initial_map.paint):
            self.set_paint(self.index_to_loc(idx), paint_val, write_fb=False)
        self.game_fb = game_fb
        self.pattern = self.create_patterns()
        self.resource_pattern_centers = []
        self.resouce_pattern_centers_by_loc = [Team.NEUTRAL] * total_area
        self.code = code
        self.debug = game_args.debug
        self.running = True
        self.robots = [None] * total_area
        self.id_to_robot: dict[int, RobotInfo] = {}
        self.robot_exec_order = []
        for robot_info in initial_map.initial_bodies:
            self.spawn_robot(robot_info.type, robot_info.location, robot_info.team, id=robot_info.id)

    def run_round(self):
        if self.running:
            self.round += 1
            self.game_fb.start_round(self.round)
            self.update_resource_patterns()
            self.each_robot(lambda robot: robot.process_beginning_of_round())
            self.each_robot_update(lambda robot: robot.turn())
            self.serialize_team_info()
            self.team_info.process_end_of_round()
            self.game_fb.end_round()
            if self.winner == None and self.round >= self.initial_map.rounds:
                self.run_tiebreakers()
            if self.winner != None:
                self.running = False
                self.each_robot_update(lambda robot: self.destroy_robot(robot.id))
        else:
            raise GameError('Game is not running!')

    def move_robot(self, start_loc, end_loc):
        self.add_robot_to_loc(end_loc, self.get_robot(start_loc))
        self.remove_robot_from_loc(start_loc)

    def add_robot_to_loc(self, loc, robot):
        self.robots[loc.y * self.width + loc.x] = robot

    def remove_robot_from_loc(self, loc):
        self.robots[loc.y * self.width + loc.x] = None

    def get_robot(self, loc: MapLocation) -> Robot:
        return self.robots[loc.y * self.width + loc.x]
    
    def get_robot_by_id(self, id) -> Robot:
        return self.id_to_robot.get(id, None)
    
    def has_tower(self, loc: MapLocation):
        robot = self.get_robot(loc)
        return robot and robot.type.is_tower_type()
    
    def has_ruin(self, loc: MapLocation):
        return self.ruins[loc.y * self.width + loc.x]
    
    def has_wall(self, loc: MapLocation):
        return self.walls[loc.y * self.width + loc.x]
    
    def get_paint_num(self, loc: MapLocation):
        return self.paint[loc.y * self.width + loc.x]
    
    def get_marker(self, team: Team, loc: MapLocation) -> int:
        markers = self.team_a_markers if team == Team.A else self.team_b_markers
        return markers[loc.y * self.width + loc.x]
    
    def mark_location(self, team: Team, loc: MapLocation, secondary: bool):
        markers = self.team_a_markers if team == Team.A else self.team_b_markers
        markers[loc.y * self.width + loc.x] = 2 if secondary else 1

    def get_map_info(self, team, loc): 
        idx = self.loc_to_index(loc)
        paint = self.paint[idx]
        match paint:
            case 0:
                paint_type = PaintType.EMPTY
            case 1:
                paint_type = PaintType.ALLY_PRIMARY if team == Team.A else PaintType.ENEMY_PRIMARY
            case 2:
                paint_type = PaintType.ALLY_SECONDARY if team == Team.A else PaintType.ENEMY_SECONDARY
            case 3:
                paint_type = PaintType.ENEMY_PRIMARY if team == Team.A else PaintType.ALLY_PRIMARY
            case 4:
                paint_type = PaintType.ENEMY_SECONDARY if team == Team.A else PaintType.ALLY_SECONDARY
        mark = self.team_a_markers[idx] if team == Team.A else self.team_b_markers[idx]
        match mark:
            case 0:
                mark_type = PaintType.EMPTY
            case 1:
                mark_type = PaintType.ALLY_PRIMARY
            case 2:
                mark_type = PaintType.ALLY_SECONDARY
        passable = not self.walls[idx] and not self.ruins[idx]
        return MapInfo(loc, passable, self.walls[idx], paint_type, mark_type, self.ruins[idx])

    def spawn_robot(self, type: UnitType, loc: MapLocation, team: Team, id=None):
        if id is None:
            id = self.id_generator.next_id()
        robot = Robot(self, id, team, type, loc)
        rc = RobotController(self, robot)
        robot.animate(self.code[team.value], self.create_methods(rc), debug=self.debug)
        self.robot_exec_order.append(id)
        self.id_to_robot[id] = robot
        self.add_robot_to_loc(loc, robot)
        return robot

    def destroy_robot(self, id):
        robot: Robot = self.id_to_robot[id]
        self.robot_exec_order.remove(id)
        del self.id_to_robot[id]
        self.remove_robot_from_loc(robot.loc)
        robot.kill()
        self.game_fb.add_die_action(id, False)
        self.game_fb.add_died(id)

    def set_winner_if_paint_percent_reached(self, team):
        if self.team_info.get_tiles_painted(team) / self.area_without_walls * 100 >= GameConstants.PAINT_PERCENT_TO_WIN:
            self.set_winner(team, DominationFactor.PAINT_ENOUGH_AREA)
            return True
        return False

    def set_winner_if_more_area(self):
        painted_a = self.team_info.get_tiles_painted(Team.A)
        painted_b = self.team_info.get_tiles_painted(Team.B)
        if painted_a == painted_b:
            return False
        self.set_winner(Team.A if painted_a > painted_b else Team.B, DominationFactor.MORE_SQUARES_PAINTED)
        return True
    
    def set_winner_if_more_allied_towers(self):
        towers_a = [robot.team == Team.A and robot.type.is_tower_type() for robot in self.id_to_robot.values()].count(True)
        towers_b = [robot.team == Team.B and robot.type.is_tower_type() for robot in self.id_to_robot.values()].count(True)
        if towers_a == towers_b:
            return False
        self.set_winner(Team.A if towers_a > towers_b else Team.B, DominationFactor.MORE_TOWERS_ALIVE)
        return True
    
    def set_winner_if_more_money(self):
        money_a = self.team_info.get_coins(Team.A)
        money_b = self.team_info.get_coins(Team.B)
        if money_a == money_b:
            return False
        self.set_winner(Team.A if money_a > money_b else Team.B, DominationFactor.MORE_MONEY)
        return True
    
    def set_winner_if_more_paint(self):
        paint_a = self.team_info.get_paint_counts(Team.A)
        paint_b = self.team_info.get_paint_counts(Team.B)
        if paint_a == paint_b:
            return False
        self.set_winner(Team.A if paint_a > paint_b else Team.B, DominationFactor.MORE_PAINT_IN_UNITS)
        return True
    
    def set_winner_if_more_alive_units(self):
        allied_a = [robot.team == Team.A and robot.type.is_robot_type() for robot in self.id_to_robot.values()].count(True)
        allied_b = [robot.team == Team.B and robot.type.is_robot_type() for robot in self.id_to_robot.values()].count(True)
        if allied_a == allied_b:
            return False
        self.set_winner(Team.A if allied_a > allied_b else Team.B, DominationFactor.MORE_ROBOTS_ALIVE)
        return True
    
    def set_winner_arbitrary(self):
        self.set_winner(Team.A if random.random() < 0.5 else Team.B, DominationFactor.WON_BY_DUBIOUS_REASONS)
        return True

    def run_tiebreakers(self):
        if self.set_winner_if_more_area(): return
        if self.set_winner_if_more_allied_towers(): return
        if self.set_winner_if_more_money(): return
        if self.set_winner_if_more_paint(): return
        if self.set_winner_if_more_alive_units(): return
        self.set_winner_arbitrary()
    
    def set_winner(self, team, domination_factor):
        self.winner = team
        self.domination_factor = domination_factor

    def update_resource_patterns(self):
        for i, center in enumerate(self.resource_pattern_centers):
            team = self.resouce_pattern_centers_by_loc[self.loc_to_index(center)]
            if self.detect_pattern(center, team) != Shape.RESOURCE:
                self.resource_pattern_centers.pop(i)
                self.resouce_pattern_centers_by_loc[self.loc_to_index(center)] = Team.NEUTRAL

    def serialize_team_info(self):
        coverage_a = math.floor(self.team_info.get_tiles_painted(Team.A) / self.area_without_walls * 1000)
        coverage_b = math.floor(self.team_info.get_tiles_painted(Team.B) / self.area_without_walls * 1000)
        self.game_fb.add_team_info(Team.A, self.team_info.get_coins(Team.A), coverage_a, self.count_resource_patterns(Team.A))
        self.game_fb.add_team_info(Team.B, self.team_info.get_coins(Team.B), coverage_b, self.count_resource_patterns(Team.B))

    def complete_resource_pattern(self, team, loc):
        idx = self.loc_to_index(loc)
        if self.resouce_pattern_centers_by_loc[idx] != Team.NEUTRAL:
            return
        self.resource_pattern_centers.append(loc)
        self.resouce_pattern_centers_by_loc[idx] = team

    def count_resource_patterns(self, team):
        return [self.resouce_pattern_centers_by_loc[self.loc_to_index(loc)] == team for loc in self.resource_pattern_centers].count(True)

    def on_the_map(self, loc: MapLocation):
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height
    
    def connected_by_paint(self, robot_loc: MapLocation, tower_loc: MapLocation, team: Team):
        queue = [robot_loc]
        visited = set()

        cardinal_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
        while queue:
            loc = queue.pop(0)
            if loc.equals(tower_loc):
                return True

            if loc in visited or self.team_from_paint(self.paint[self.loc_to_index(loc)]) != team:
                continue

            visited.add(loc)
            for dir in cardinal_directions:
                new_loc = loc.add(dir)  

                if self.on_the_map(new_loc):
                    queue.append(new_loc)
        return False
    
    def update_resource_patterns(self):
        pass
        
    def get_primary_paint(self, team):
        """
        Returns the primary paint value for a given team.
        """
        if team == Team.A:
            return 1
        elif team == Team.B:
            return 3
        return 0

    def get_secondary_paint(self, team):
        """
        Returns the secondary paint value for a given team.
        """
        if team == Team.A:
            return 2
        elif team == Team.B:
            return 4
        return 0

    def team_from_paint(self, paint):
        """
        Determines the team based on the paint value.
        """
        if paint == 1 or paint == 2:
            return Team.A
        elif paint == 3 or paint == 4:
            return Team.B
        else:
            return Team.NEUTRAL
        
    def is_primary_paint(self, paint):
        return paint == 1 or paint == 3

    def get_paint_type(self, team, loc):
        paint = self.paint[self.loc_to_index(loc)]
        paint_team = self.team_from_paint(paint)
        if paint_team == Team.NEUTRAL:
            return PaintType.EMPTY
        elif paint_team == team:
            return PaintType.ALLY_PRIMARY if self.is_primary_paint(paint) else PaintType.ALLY_SECONDARY
        else:
            return PaintType.ENEMY_PRIMARY if self.is_primary_paint(paint) else PaintType.ENEMY_SECONDARY
        
    def shape_from_tower_type(self, tower_type):
        if tower_type in {UnitType.LEVEL_ONE_PAINT_TOWER, UnitType.LEVEL_TWO_PAINT_TOWER, UnitType.LEVEL_THREE_PAINT_TOWER}:
            return Shape.PAINT_TOWER
        if tower_type in {UnitType.LEVEL_ONE_DEFENSE_TOWER, UnitType.LEVEL_TWO_DEFENSE_TOWER, UnitType.LEVEL_THREE_DEFENSE_TOWER}:
            return Shape.DEFENSE_TOWER
        if tower_type in {UnitType.LEVEL_ONE_MONEY_TOWER, UnitType.LEVEL_TWO_MONEY_TOWER, UnitType.LEVEL_THREE_MONEY_TOWER}:
            return Shape.MONEY_TOWER
        return None
        
    def set_paint(self, loc, paint, write_fb=True):
        idx = self.loc_to_index(loc)
        if self.walls[idx] or self.ruins[idx]: return

        old_paint_team = self.team_from_paint(self.paint[idx])
        new_paint_team = self.team_from_paint(paint)

        if old_paint_team != Team.NEUTRAL:
            self.team_info.add_painted_squares(-1, old_paint_team)
        if new_paint_team != Team.NEUTRAL:
            self.team_info.add_painted_squares(1, new_paint_team)
        self.paint[idx] = paint

        if write_fb:
            if paint != 0:
                self.game_fb.add_paint_action(loc, not self.is_primary_paint(paint))
            else:
                self.game_fb.add_unpaint_action(loc)

        if new_paint_team != Team.NEUTRAL:
            self.set_winner_if_paint_percent_reached(new_paint_team)

    def get_all_locations_within_radius_squared(self, center: MapLocation, radius_squared) -> Generator[MapLocation, None, None]:
        """
        center: MapLocation object
        radius_squared: square of radius around center that we want locations for

        Returns a list of MapLocations within radius squared of center
        """
        cx = center.x
        cy = center.y
        ceiled_radius = math.ceil(math.sqrt(radius_squared)) # add +1 just to be safe
        min_x = max(cx - ceiled_radius, 0)
        min_y = max(cy - ceiled_radius, 0)
        max_x = min(cx + ceiled_radius, self.width - 1)
        max_y = min(cy + ceiled_radius, self.height - 1)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if (cx - x) ** 2 + (cy - y) ** 2 <= radius_squared:
                    yield MapLocation(x, y)

    def is_valid_pattern_center(self, center):
        '''
        Checks if pattern centered at this location would be in the bounds of the map
        '''
        offset = GameConstants.PATTERN_SIZE // 2
        shape_out_of_bounds = (center.x + offset >= self.width or 
                               center.x - offset < 0 or 
                               center.y + offset >= self.height or 
                               center.y - offset < 0)
        return not shape_out_of_bounds
    
    def mark_pattern(self, team: Team, center: MapLocation, shape: Shape):
        '''
        Marks pattern at center
        '''
        pattern_array = self.pattern[shape.value]
        offset = GameConstants.PATTERN_SIZE//2
        for row in range(-offset, offset + 1):
            for col in range(-offset, offset + 1):
                loc = MapLocation(center.x + col, center.y + row)
                if self.ruins[self.loc_to_index(loc)]:
                    continue
                secondary = pattern_array[row + offset][col + offset]
                self.mark_location(team, loc, secondary)
                self.game_fb.add_mark_action(loc, secondary)        

    def mark_tower_pattern(self, team, center, tower_type):
        '''
        Marks specified tower pattern at center
        tower_type: tower_type: RobotType enum
        '''
        self.mark_pattern(team, center, self.shape_from_tower_type(tower_type))

    def simple_check_pattern(self, center, shape, team):
        offset = GameConstants.PATTERN_SIZE//2
        pattern_array = self.pattern[shape.value]
        for dx in range(-offset, offset + 1):
            for dy in range(-offset, offset + 1):
                map_loc = MapLocation(center.x + dx, center.y + dy)
                if self.has_ruin(map_loc):
                    continue
                actual_paint = self.paint[self.loc_to_index(map_loc)]
                if self.team_from_paint(actual_paint) != team:
                    return False
                secondary_actual = not self.is_primary_paint(actual_paint)
                secondary_pattern = pattern_array[dy + offset][dx + offset]
                if secondary_actual != secondary_pattern:
                    return False
        return True

    def mark_resource_pattern(self, team, center):
        '''
        Marks resource pattern at center
        '''
        self.mark_pattern(team, center, Shape.RESOURCE)

    def detect_pattern(self, center, team):
        '''
        Check if there is any transformation of a 5x5 pattern centered at "center" for a particular team
        Returns detected pattern type (as Shape Enum), or None if there is no pattern
        '''
        class Transformation(Enum):
            ORIGINAL = 0
            FLIP_X = 1
            FLIP_Y = 2
            FLIP_D1 = 3
            FLIP_D2 = 4
            ROTATE_90 = 5
            ROTATE_180 = 6
            ROTATE_270 = 7
        
        if not self.is_valid_pattern_center(center):
            return None
        
        patterns_list = list(Shape.__members__.values()) # list of Shape enum members 

        def check_pattern(shape: Shape): 
            debug_str = ""
            '''
            Check presence of a particular pattern type up to 8 symmetries
            Returns True/False, whether pattern is present
            '''
            pattern_array = self.pattern[shape.value]
            valid_transformations = [True] * len(Transformation) # T/F for whether a transformation is valid

            offset = GameConstants.PATTERN_SIZE//2

            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    for variant in list(Transformation.__members__.values()):
                        if(variant == Transformation.ORIGINAL):
                            dx_ = dx
                            dy_ = dy
                        elif(variant == Transformation.FLIP_X):
                            dx_ = -dx
                            dy_ = dy
                        elif(variant == Transformation.FLIP_Y):
                            dx_ = dx
                            dy_ = -dy
                        elif(variant == Transformation.FLIP_D1): 
                            dx_ = dy
                            dy_ = dx
                        elif(variant == Transformation.FLIP_D2): 
                            dx_ = -dy
                            dy_ = -dx
                        elif(variant == Transformation.ROTATE_90):
                            dx_ = -dy
                            dy_ = dx
                        elif(variant == Transformation.ROTATE_180):
                            dx_ = -dx
                            dy_ = -dy
                        elif(variant == Transformation.ROTATE_270):
                            dx_ = dy
                            dy_ = -dx

                        map_loc = MapLocation(center.x + dx_, center.y + dy_) # location on map after transforming pattern
                        actual_paint = self.paint[self.loc_to_index(map_loc)]
                        
                        if(self.team_from_paint(actual_paint) != team): # wrong team
                            valid_transformations[shape.value] = False
                        
                        #assumes pattern arrays have True as secondary, False as primary
                        secondary_actual = not self.is_primary_paint(actual_paint)
                        secondary_pattern = pattern_array[dy + offset][dx + offset]
                        if secondary_actual != secondary_pattern and not self.has_ruin(map_loc):
                            valid_transformations[variant.value] = False

            return any(valid_transformations)
        
        for shape in patterns_list: 
            if(check_pattern(shape)):
                return shape
        return None
    
    def create_pattern_array(self, pattern):
        result = [[0 for i in range(GameConstants.PATTERN_SIZE)] for j in range(GameConstants.PATTERN_SIZE)]
        for i in range(GameConstants.PATTERN_SIZE ** 2):
            x = i // GameConstants.PATTERN_SIZE
            y = i % GameConstants.PATTERN_SIZE
            result[x][y] = (pattern >> i) & 1
        return result

    def create_test_pattern_array(self):
        result = [[0 for i in range(GameConstants.PATTERN_SIZE)] for j in range(GameConstants.PATTERN_SIZE)]
        for i in range(GameConstants.PATTERN_SIZE ** 2):
            x = i // GameConstants.PATTERN_SIZE
            y = i % GameConstants.PATTERN_SIZE
            result[x][y] = i % 2
        return result
    
    def is_passable(self, loc):
        idx = self.loc_to_index(loc)
        return not self.walls[idx] and not self.ruins[idx]
    
    def loc_to_index(self, loc):
        return loc.y * self.width + loc.x
    
    def index_to_loc(self, idx):
        return MapLocation(idx % self.width, idx // self.width)
        
    def log_info(self, msg):
        print(f'\u001b[32m[Game info] {msg}\u001b[0m')

    def each_robot(self, func):
        for robot in self.id_to_robot.values():
            func(robot)

    def each_robot_update(self, func):
        exec_order = self.robot_exec_order[:]
        for id in exec_order:
            if id in self.id_to_robot:
                func(self.id_to_robot[id])

    def create_methods(self, rc: RobotController):
        return {
            'GameError': GameError,
            'UnitType': UnitType,
            'RobotError': RobotError,
            'Team': Team,
            'Direction': Direction,
            'MapLocation': MapLocation,
            'RobotInfo': RobotInfo,
            'MapInfo': MapInfo,
            'PaintType': PaintType,
            'Message': Message,
            'get_round_num': (rc.get_round_num, 1),
            'get_map_width': (rc.get_map_width, 1),
            'get_map_height': (rc.get_map_height, 1),
            'get_resource_pattern': (rc.get_resource_pattern, 2),
            'get_tower_pattern': (rc.get_tower_pattern, 2),
            'get_id': (rc.get_id, 1),
            'get_team': (rc.get_team, 1),
            'get_location': (rc.get_location, 1),
            'get_health': (rc.get_health, 1),
            'get_paint': (rc.get_paint, 1),
            'get_money': (rc.get_money, 1),
            'get_type': (rc.get_type, 1),
            'on_the_map': (rc.on_the_map, 5),
            'can_sense_location': (rc.can_sense_location, 5),
            'is_location_occupied': (rc.is_location_occupied, 5),
            'can_sense_robot_at_location': (rc.can_sense_robot_at_location, 5),
            'sense_robot_at_location': (rc.sense_robot_at_location, 15),
            'can_sense_robot': (rc.can_sense_robot, 5),
            'sense_robot': (rc.sense_robot, 25),
            'sense_nearby_robots': (rc.sense_nearby_robots, 100),
            'sense_passability': (rc.sense_passability, 5),
            'sense_nearby_ruins': (rc.sense_nearby_ruins, 100),
            'sense_map_info': (rc.sense_map_info, 5),
            'sense_nearby_map_infos': (rc.sense_nearby_map_infos, 100),
            'adjacent_location': (rc.adjacent_location, 1),
            'get_all_locations_within_radius_squared': (rc.get_all_locations_within_radius_squared, 100),
            'is_action_ready': (rc.is_action_ready, 1),
            'get_action_cooldown_turns': (rc.get_action_cooldown_turns, 1),
            'is_movement_ready': (rc.is_movement_ready, 1),
            'get_movement_cooldown_turns': (rc.get_movement_cooldown_turns, 1),
            'can_move': (rc.can_move, 10),
            'move': rc.move,
            'can_build_robot': (rc.can_build_robot, 10),
            'build_robot': (rc.build_robot, 20),
            'can_mark': (rc.can_mark, 5),
            'mark': (rc.mark, 5),
            'can_remove_mark': (rc.can_remove_mark, 5),
            'remove_mark': (rc.remove_mark, 5),
            'can_mark_tower_pattern': (rc.can_mark_tower_pattern, 50),
            'mark_tower_pattern': (rc.mark_tower_pattern, 50),
            'can_mark_resource_pattern': (rc.can_mark_resource_pattern, 50),
            'mark_resource_pattern': (rc.mark_resource_pattern, 50),
            'can_complete_tower_pattern': (rc.can_complete_tower_pattern, 50),
            'complete_tower_pattern': (rc.complete_tower_pattern, 50),
            'can_complete_resource_pattern': (rc.can_complete_resource_pattern, 50),
            'complete_resource_pattern': (rc.complete_resource_pattern, 50),
            'can_attack': (rc.can_attack, 10),
            'attack': rc.attack,
            'can_mop_swing': (rc.can_mop_swing, 10),
            'mop_swing': rc.mop_swing,
            'can_send_message': (rc.can_send_message, 50),
            'send_message': (rc.send_message, 50),
            'read_messages': (rc.read_messages, 10),
            'can_transfer_paint': (rc.can_transfer_paint, 5),
            'transfer_paint': (rc.transfer_paint, 5),
            'can_upgrade_tower': (rc.can_upgrade_tower, 2),
            'upgrade_tower': rc.upgrade_tower,
            'resign': rc.resign,
            'set_indicator_string': rc.set_indicator_string,
            'set_indicator_dot': rc.set_indicator_dot,
            'set_indicator_line': rc.set_indicator_line,
            'set_timeline_marker': rc.set_timeline_marker,
        }
    
    def create_patterns(self):
        resource_pattern = [
            [True, False, True, False, True],
            [False, True, False, True, False],
            [True, False, True, False, True],
            [False, True, False, True, False],
            [True, False, True, False, True]
        ]
        money_tower_pattern = [
            [False, True, True, True, False],
            [True, True, False, True, True],
            [True, False, False, False, True],
            [True, True, False, True, True],
            [False, True, True, True, False]
        ]
        paint_tower_pattern = [
            [True, False, False, False, True],
            [False, True, False, True, False],
            [False, False, True, False, False],
            [False, True, False, True, False],
            [True, False, False, False, True]
        ]
        defense_tower_pattern = [
            [False, False, True, False, False],
            [False, True, True, True, False],
            [True, True, True, True, True],
            [False, True, True, True, False],
            [False, False, True, False, False]
        ]
        return resource_pattern, defense_tower_pattern, money_tower_pattern, paint_tower_pattern

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass

class GameError(Exception):
    """Raised for errors that arise within the Game"""
    pass
