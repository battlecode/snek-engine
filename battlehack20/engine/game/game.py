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

import math

class DominationFactor(Enum):
    PAINTED_AREA=0
    NUM_ALLIED_TOWERS=1
    TOTAL_MONEY=2
    TOTAL_PAINT=3
    NUM_ALIVE_UNITS=4
    RESIGNATION=5
    RANDOM=6

class Shape(Enum): # marker shapes
    STAR=0
    SMILE=1
    CIRCLE=2
    SQUARE=3
    DIAMOND=4

class Game:

    def __init__(self, code, initial_map: InitialMap, match_maker: GameFB, debug=False):
        random.seed(GameConstants.GAME_DEFAULT_SEED)
        self.width = initial_map.width
        self.height = initial_map.height
        total_area = self.width * self.height
        self.area_without_walls = total_area - sum(initial_map.walls)
        self.walls = initial_map.walls
        self.markers = [0] * total_area
        self.current_round = 0
        self.id_generator = IDGenerator()
        self.winner = None
        self.domination_factor = None
        self.initial_map = initial_map
        self.paint = [0] * total_area
        self.team_info = TeamInfo(self)
        self.team_info.add_coins(Team.A, GameConstants.INITIAL_TEAM_MONEY)
        self.team_info.add_coins(Team.B, GameConstants.INITIAL_TEAM_MONEY)
        self.match_maker = match_maker
        self.pattern = initial_map.pattern
        self.resource_pattern_centers = []
        self.resource_pattern_teams = []
        self.ruins = initial_map.ruins
        self.code = code
        self.debug = debug
        self.running = True
        self.robots = [None] * total_area
        self.id_to_robot = {}
        self.robot_exec_order = []
        for robot_info in initial_map.initial_bodies:
            self.spawn_robot(robot_info.robot_type, robot_info.location, robot_info.team)

    def turn(self):
        if self.running:
            self.round += 1

            if self.round > self.max_rounds:
                self.check_over()

            if self.debug:
                self.log_info(f'Turn {self.round}')
                self.log_info(f'Queue: {self.queue}')
                self.log_info(f'Lords: {self.lords}')

            for id, robot in self.board_statesqueue.items():
                robot.turn()
                if not robot.runner.initialized:
                    self.delete_robot(id)
                self.check_over()

            if self.running:
                for robot in self.lords:
                    robot.turn()

                self.lords.reverse()  # the HQ's will alternate spawn order
        else:
            raise GameError('')

    def move_robot(self, start_loc, end_loc):
        self.add_robot_to_loc(end_loc, self.get_robot(start_loc))
        self.remove_robot_from_loc(start_loc)

    def add_robot_to_loc(self, loc, robot):
        self.robots[self.loc_to_index(loc)] = robot

    def remove_robot_from_loc(self, loc):
        self.robots[self.loc_to_index(loc)] = None

    def get_robot(self, loc: MapLocation):
        return self.robots[self.loc_to_index(loc)]

    def spawn_robot(self, type: RobotType, loc: MapLocation, team: Team):
        id = self.id_generator.next_id()
        robot = Robot(self, id, team, type, loc)

        #TODO totally broken :/
        methods = {
            'GameError': GameError,
            'RobotType': RobotType,
            'RobotError': RobotError,
            'Team': Team,
            'get_board_size': lambda : get_board_size(self),
            'get_bytecode' : lambda : robot.runner.bytecode,
            'get_team': lambda : get_team(self, robot),
            'get_type': lambda: get_type(self, robot),
            'capture': lambda row, col: capture(self, robot, row, col),
            'check_space': lambda row, col: pawn_check_space(self, robot, row, col),
            'get_location': lambda : get_location(self, robot),
            'move_forward': lambda: move_forward(self, robot),
            'sense': lambda : sense(self, robot)
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
        robot.kill()

    # def setWinnerIfPaintPercentReached(self, team):
    #     # this.totalPaintedSquares[team.ordinal()] += num;
    #     # int areaWithoutWalls = this.gameWorld.getAreaWithoutWalls();
    #     # if (this.totalPaintedSquares[team.ordinal()] / (double) areaWithoutWalls * 100 >= GameConstants.PAINT_PERCENT_TO_WIN) {
    #     #     checkWin(team);
    #     # }

    def setWinnerIfMoreArea(self):
        if self.team_info.get_tiles_painted(Team.BLACK) > self.teamInfo.get_tiles_painted(Team.BLACK):
            self.set_winner(Team.WHITE, DominationFactor.PAINTED_AREA)
        elif self.team_info.get_tiles_painted(Team.BLACK) < self.teamInfo.get_tiles_painted(Team.BLACK):
            self.set_winner(Team.BLACK, DominationFactor.PAINTED_AREA)
        else:
            return False
        return True
    
    def setWinnerIfMoreAlliedTowers(self):
        if self.team_info.get_num_allied_towers(Team.BLACK) > self.team_info.get_num_allied_towers(Team.BLACK):
            self.set_winner(Team.WHITE, DominationFactor.NUM_ALLIED_TOWERS)
        elif self.team_info.get_num_allied_towers(Team.BLACK) < self.team_info.get_num_allied_towers(Team.BLACK):
            self.set_winner(Team.BLACK, DominationFactor.NUM_ALLIED_TOWERS)
        else:
            return False
        return True
    
    def setWinnerIfMoreMoney(self):
        if self.team_info.get_num_allied_towers(Team.WHITE) > self.team_info.get_num_allied_towers(Team.BLACK):
            self.set_winner(Team.WHITE, DominationFactor.TOTAL_MONEY)
        elif self.team_info.get_num_allied_towers(Team.WHITE) < self.team_info.get_num_allied_towers(Team.BLACK):
            self.set_winner(Team.BLACK, DominationFactor.TOTAL_MONEY)
        else:
            return False
        return True
    
    def setWinnerIfMorePaint(self):
        if self.team_info.get_paint_counts(Team.WHITE) > self.team_info.get_paint_counts(Team.BLACK):
            self.set_winner(Team.WHITE, DominationFactor.TOTAL_PAINT)
        elif self.team_info.get_paint_counts(Team.WHITE) < self.team_info.get_paint_counts(Team.BLACK):
            self.set_winner(Team.BLACK, DominationFactor.TOTAL_PAINT)
        else:
            return False
        return True
    
    def setWinnerIfMoreAliveUnits(self):
        if self.team_info.get_num_allied_units(Team.WHITE) > self.team_info.get_num_allied_units(Team.BLACK):
            self.set_winner(Team.WHITE, DominationFactor.NUM_ALIVE_UNITS)
        elif self.team_info.get_num_allied_units(Team.WHITE) < self.team_info.get_num_allied_units(Team.BLACK):
            self.set_winner(Team.BLACK, DominationFactor.NUM_ALIVE_UNITS)
        else:
            return False
        return True
    
    def setWinnerArbitrary(self):
        rand_num = random.random()
        if rand_num < 0.5:
            self.set_winner(Team.WHITE, DominationFactor.RANDOM)
        else:
           self.set_winner(Team.BLACK, DominationFactor.RANDOM)

    def check_over(self):
        if (self.round_number == self.max_rounds and not self.winner):
            if self.setWinnerIfMoreArea(): return
            if self.setWinnerIfMoreAlliedTowers(): return
            if self.setWinnerIfMoreMoney(): return
            if self.setWinnerIfMorePaint(): return
            if self.setWinnerIfMoreAliveUnits(): return
            if self.setWinnerArbitrary(): return
        self.setWinnerArbitrary()

    def process_over(self):
        """
        Helper method to process once a game is finished (e.g. deleting robots)
        """
        for id, robot in self.queue.items():
            self.delete_robot(id)
    
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

                if on_the_map(new_loc.x, new_loc.y):  
                    queue.append(new_loc)
        return False
        
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

    #### DEBUG METHODS: NOT AVAILABLE DURING CONTEST ####

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

    def get_all_locations_within_radius_squared(self, center, radius_squared):
        """
        center: MapLocation object
        radius_squared: square of radius around center that we want locations for

        Returns a list of MapLocations within radius squared of center
        """
        return_locations = []
        width = self.width
        height = self.height
        ceiled_radius = math.ceil(math.sqrt(radius_squared)) + 1 # add +1 just to be safe
        minX = max(center.x - ceiled_radius, 0)
        minY = max(center.y - ceiled_radius, 0)
        maxX = min(center.x + ceiled_radius, width - 1)
        maxY = min(center.y + ceiled_radius, height - 1)

        for x in range(minX, maxX + 1):
            for y in range(minY, maxY + 1):
                new_location = MapLocation(x, y) 
                if center.is_within_distance_squared(new_location, radius_squared):
                    return_locations.append(new_location)
        return return_locations
      
    def mark_location(self, loc, color):
        self.markers[self.loc_to_index(loc)] = color
    
    def is_passable(self, loc):
        idx = self.loc_to_index(loc)
        return not self.walls[idx] and self.robots[idx] == None
  
    def get_robot_by_id(self, id):
        for i in range(self.height):
            for j in range(self.width):
                res = self.robots[i][j]
                if isinstance(res, Robot) and res.id == id:
                    return res
        return None
  
    def get_map_info(self, loc): 
        passable = self.is_passable(loc)
        is_ruins = self.ruins[loc.x][loc.y]
        paint_color = self.paint[loc.x][loc.y]
        robot_type = self.robots[loc.x][loc.y]
        return MapInfo(loc, passable, is_ruins, paint_color, robot_type)
    
    def loc_to_index(self, loc):
        return loc.y * self.width + loc.x
    
    def coord_to_index(self, x, y):
        return y * self.width + x
    
    def log_info(self, msg):
        print(f'\u001b[32m[Game info] {msg}\u001b[0m')

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass

class GameError(Exception):
    """Raised for errors that arise within the Game"""
    pass
