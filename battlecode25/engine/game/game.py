import random
from enum import Enum
from .robot import Robot
from .team import Team
from .robot_type import RobotType
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

import math

class Shape(Enum): # marker shapes
    STAR=0
    SMILE=1
    CIRCLE=2
    SQUARE=3
    DIAMOND=4

class Game:

    def __init__(self, code, initial_map: InitialMap, game_fb: GameFB, game_args):
        random.seed(GameConstants.GAME_DEFAULT_SEED)
        self.width = initial_map.width
        self.height = initial_map.height
        total_area = self.width * self.height
        self.area_without_walls = total_area - sum(initial_map.walls)
        self.walls = initial_map.walls
        self.markers = [0] * total_area
        self.round = 0
        self.id_generator = IDGenerator()
        self.winner = None
        self.domination_factor = None
        self.initial_map = initial_map
        self.paint = [0] * total_area
        self.team_info = TeamInfo(self)
        self.team_info.add_coins(Team.A, GameConstants.INITIAL_TEAM_MONEY)
        self.team_info.add_coins(Team.B, GameConstants.INITIAL_TEAM_MONEY)
        self.game_fb = game_fb
        self.pattern = initial_map.pattern
        self.resource_pattern_centers = []
        self.resource_pattern_teams = []
        self.ruins = initial_map.ruins
        self.code = code
        self.debug = game_args.debug
        self.running = True
        self.robots = [None] * total_area
        self.id_to_robot = {}
        self.robot_exec_order = []
        for robot_info in initial_map.initial_bodies:
            self.spawn_robot(robot_info.type, robot_info.location, robot_info.team, id=robot_info.id)

    def run_round(self):
        if self.running:
            self.round += 1
            self.game_fb.start_round(self.round)
            self.each_robot(lambda robot: robot.process_beginning_of_round())
            self.update_resource_patterns()
            self.each_robot_update(lambda robot: robot.turn())
            self.game_fb.add_team_info(Team.A, self.team_info.get_coins(Team.A))
            self.game_fb.add_team_info(Team.B, self.team_info.get_coins(Team.B))
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
        self.robots[self.loc_to_index(loc)] = robot

    def remove_robot_from_loc(self, loc):
        self.robots[self.loc_to_index(loc)] = None

    def get_robot(self, loc: MapLocation):
        return self.robots[self.loc_to_index(loc)]

    def spawn_robot(self, type: RobotType, loc: MapLocation, team: Team, id=None):
        if id is None:
            id = self.id_generator.next_id()
        robot = Robot(self, id, team, type, loc)
        rc = RobotController(self, robot)

        methods = {
            'GameError': GameError,
            'RobotType': RobotType,
            'RobotError': RobotError,
            'Team': Team,
            'get_location': rc.get_location,
            'get_map_width': rc.get_map_width,
            'get_map_height': rc.get_map_height,
            'get_team': rc.get_team,
            'can_move': rc.can_move,
            'move': rc.move,
            'Direction': Direction
        }

        robot.animate(self.code[team.value], methods, debug=self.debug)
        self.robot_exec_order.append(id)
        self.id_to_robot[id] = robot
        self.add_robot_to_loc(loc, robot)

    def destroy_robot(self, id):
        robot: Robot = self.id_to_robot[id]
        self.robot_exec_order.remove(id)
        del self.id_to_robot[id]
        self.remove_robot_from_loc(robot.loc)

    def setWinnerIfPaintPercentReached(self, team):
        if self.team_info.get_tiles_painted(team) / self.area_without_walls * 100 >= GameConstants.PAINT_PERCENT_TO_WIN:
            self.set_winner(team, DominationFactor.PAINT_ENOUGH_AREA)
            return True
        return False

    def setWinnerIfMoreArea(self):
        painted_a = self.team_info.get_tiles_painted(Team.A)
        painted_b = self.team_info.get_tiles_painted(Team.B)
        if painted_a == painted_b:
            return False
        self.set_winner(Team.A if painted_a > painted_b else Team.B, DominationFactor.MORE_SQUARES_PAINTED)
        return True
    
    def setWinnerIfMoreAlliedTowers(self):
        towers_a = self.team_info.get_num_allied_towers(Team.A)
        towers_b = self.team_info.get_num_allied_towers(Team.B)
        if towers_a == towers_b:
            return False
        self.set_winner(Team.A if towers_a > towers_b else Team.B, DominationFactor.MORE_TOWERS_ALIVE)
        return True
    
    def setWinnerIfMoreMoney(self):
        money_a = self.team_info.get_coins(Team.A)
        money_b = self.team_info.get_coins(Team.B)
        if money_a == money_b:
            return False
        self.set_winner(Team.A if money_a > money_b else Team.B, DominationFactor.MORE_MONEY)
        return True
    
    def setWinnerIfMorePaint(self):
        paint_a = self.team_info.get_paint_counts(Team.A)
        paint_b = self.team_info.get_paint_counts(Team.B)
        if paint_a == paint_b:
            return False
        self.set_winner(Team.A if paint_a > paint_b else Team.B, DominationFactor.MORE_PAINT_IN_UNITS)
        return True
    
    def setWinnerIfMoreAliveUnits(self):
        allied_a = self.team_info.get_num_allied_units(Team.A)
        allied_b = self.team_info.get_num_allied_units(Team.B)
        if allied_a == allied_b:
            return False
        self.set_winner(Team.A if allied_a > allied_b else Team.B, DominationFactor.MORE_ROBOTS_ALIVE)
        return True
    
    def setWinnerArbitrary(self):
        self.set_winner(Team.A if random.random() < 0.5 else Team.B, DominationFactor.WON_BY_DUBIOUS_REASONS)
        return True

    def run_tiebreakers(self):
        if self.setWinnerIfMoreArea(): return
        if self.setWinnerIfMoreAlliedTowers(): return
        if self.setWinnerIfMoreMoney(): return
        if self.setWinnerIfMorePaint(): return
        if self.setWinnerIfMoreAliveUnits(): return
        if self.setWinnerArbitrary(): return
        self.setWinnerArbitrary()
    
    def set_winner(self, team, domination_factor):
        self.winner = team
        self.domination_factor = domination_factor

    def on_the_map(self, loc):
        return 0 <= loc.x < self.width and 0 <= loc.y < self.height
    
    def flood_fill(self, robot_loc, tower_loc):
        queue = [robot_loc]
        visited = set()

        cardinal_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
        while queue:
            loc = queue.pop(0)
            if loc.equals(tower_loc):
                return True

            if loc in visited or self.paint[self.loc_to_index(loc)] != robot_loc.team:
                continue

            visited.add(loc)
            for dir in cardinal_directions:
                new_loc = loc.add(dir)  

                if self.on_the_map(new_loc.x, new_loc.y):  
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
            return 0
        
    def set_paint(self, loc, paint):
        idx = self.loc_to_index(loc)
        old_paint_team = self.team_from_paint(self.paint[idx])
        new_paint_team = self.team_from_paint(paint)

        if old_paint_team != Team.NEUTRAL:
            self.team_info.add_painted_squares(-1, old_paint_team)

        if new_paint_team != Team.NEUTRAL:
            self.team_info.add_painted_squares(1, new_paint_team)

        self.paint[idx] = paint

    def get_all_locations_within_radius_squared(self, center: MapLocation, radius_squared):
        """
        center: MapLocation object
        radius_squared: square of radius around center that we want locations for

        Returns a list of MapLocations within radius squared of center
        """
        return_locations = []
        ceiled_radius = math.ceil(math.sqrt(radius_squared)) + 1 # add +1 just to be safe
        min_x = max(center.x - ceiled_radius, 0)
        min_y = max(center.y - ceiled_radius, 0)
        max_x = min(center.x + ceiled_radius, self.width - 1)
        max_y = min(center.y + ceiled_radius, self.height - 1)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                new_location = MapLocation(x, y) 
                if center.is_within_distance_squared(new_location, radius_squared):
                    return_locations.append(new_location)
        return return_locations
      
    def mark_location(self, loc, color):
        self.markers[self.loc_to_index(loc)] = color
    
    def is_passable(self, loc):
        idx = self.loc_to_index(loc)
        return not self.walls[idx] and self.robots[idx] == None
  
    def get_map_info(self, loc): 
        idx = self.loc_to_index(loc)
        return MapInfo(loc, self.is_passable(loc), self.walls[idx], self.paint[idx], self.markers[idx], self.ruins[idx])
    
    def loc_to_index(self, loc):
        return loc.y * self.width + loc.x
    
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

    #### DEBUG METHODS ####

    def view_board(self, colors=True):
        """
        @DEBUG_METHOD
        THIS METHOD IS NOT AVAILABLE DURING ACTUAL GAMES.

        Helper method that displays the full board as a human-readable string.
        """
        board = ''
        for i in range(self.height):
            for j in range(self.width):
                if self.robots[i][j]:
                    board += '['
                    if colors:
                        if self.robots[i][j].team == Team.WHITE:
                            board += '\033[1m\u001b[37m'
                        else:
                            board += '\033[1m\u001b[36m'
                    board += str(self.robots[i][j])
                    if colors:
                        board += '\033[0m\u001b[0m] '
                else:
                    board += '[    ] '
            board += '\n'
        return board

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass

class GameError(Exception):
    """Raised for errors that arise within the Game"""
    pass
