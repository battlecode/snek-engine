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

import math
class Color(Enum): #marker and paint colors
    NONE=0
    FOREGROUND=1
    BACKGROUND=2

class DominationFactor(Enum):
    PAINTED_AREA=0
    NUM_ALLIED_TOWERS=1
    TOTAL_MONEY=2
    TOTAL_PAINT=3
    NUM_ALIVE_UNITS=4
    RANDOM=5

class Shape(Enum): # marker shapes
    STAR=0
    SMILE=1
    CIRCLE=2
    SQUARE=3
    DIAMOND=4

class Game:
    def __init__(self, code, board_width, board_height, max_rounds=GameConstants.MAX_ROUNDS, 
                 seed=GameConstants.DEFAULT_SEED, debug=False):
        random.seed(seed)
        self.code = code
        self.debug = debug
        self.running = True
        self.winner = None
        self.domination_factor = None
        self.round_number = 0

        self.robot_count = 0
        self.queue = {}
        self.board_states = [] #TODO remove

        self.board_width = board_width
        self.board_height = board_height
        self.board_size = board_width #TODO remove
        self.robots = [[None] * self.board_width for _ in range(self.board_height)]
        self.paint = [[None] * self.board_width for _ in range(self.board_height)]
        self.walls = [[None] * self.board_width for _ in range(self.board_height)]
        self.towers = [[None] * self.board_width for _ in range(self.board_height)]
        self.round = 0
        self.max_rounds = max_rounds

        self.team_info = TeamInfo(self)
        
        self.markers = {Team.WHITE: [[0]*self.board_width for i in range(self.board_height)], Team.BLACK: [[0]*self.board_width for i in range(self.board_height)]}

        self.new_robot(None, None, Team.WHITE, RobotType.OVERLORD)
        self.new_robot(None, None, Team.BLACK, RobotType.OVERLORD)

        if self.debug:
            self.log_info(f'Seed: {seed}')

    def turn(self):
        if self.running:
            self.round += 1

            if self.round > self.max_rounds:
                self.check_over()

            if self.debug:
                self.log_info(f'Turn {self.round}')
                self.log_info(f'Queue: {self.queue}')
                self.log_info(f'Lords: {self.lords}')

            for i in range(self.robot_count):
                if i in self.queue:
                    robot = self.queue[i]
                    robot.turn()

                    if not robot.runner.initialized:
                        self.delete_robot(i)
                    self.check_over()

            if self.running:
                for robot in self.lords:
                    robot.turn()

                self.lords.reverse()  # the HQ's will alternate spawn order
                self.board_states.append([row[:] for row in self.robots])
        else:
            raise GameError('game is over')

    def delete_robot(self, i):
        robot = self.queue[i]
        self.robots[robot.row][robot.col] = None
        robot.kill()
        del self.queue[i]
    
    def add_robot(self, robot):
        """Adds the new robot to the game board and increments the robot count."""
        self.robots[robot.row][robot.col] = robot
        self.queue[self.robot_count] = robot
        self.robot_count += 1
    
    def buildRobot(self, robot_type, map_location, team):
        """
        Creates and places a new robot of the specified type at the given map location.
        """
        new_robot = Robot(map_location.x, map_location.y, team, self.robot_count, robot_type)
        self.add_robot(new_robot)

    def serialize(self):
        def serialize_robot(robot):
            if robot is None:
                return None

            return {'id': robot.id, 'team': robot.team, 'health': robot.health, 'logs': robot.logs[:]}

        return [[serialize_robot(c) for c in r] for r in self.robots]

    def log_info(self, msg):
        print(f'\u001b[32m[Game info] {msg}\u001b[0m')

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
            # if game over...
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
        for i in range(self.robot_count):
            if i in self.queue:
                self.delete_robot(i)
    
    def set_winner(self, team, domination_factor):
        self.winner = team
        self.domination_factor = domination_factor

    def new_robot(self, row, col, team, robot_type):
        if robot_type == RobotType.OVERLORD:
            id = f'{team.name} HQ'
        else:
            id = self.robot_count
        robot = Robot(row, col, team, id, robot_type)

        shared_methods = {
            'GameError': GameError,
            'RobotType': RobotType,
            'RobotError': RobotError,
            'Team': Team,
            'get_board_size': lambda : get_board_size(self),
            'get_bytecode' : lambda : robot.runner.bytecode,
            'get_team': lambda : get_team(self, robot),
            'get_type': lambda: get_type(self, robot),
        }

        if robot_type == RobotType.OVERLORD:
            methods = {
                'check_space': lambda row, col: hq_check_space(self, row, col),
                'get_board': lambda : get_board(self),
                'spawn': lambda row, col: spawn(self, robot, row, col)
            }
        else:
            methods = {
                'capture': lambda row, col: capture(self, robot, row, col),
                'check_space': lambda row, col: pawn_check_space(self, robot, row, col),
                'get_location': lambda : get_location(self, robot),
                'move_forward': lambda: move_forward(self, robot),
                'sense': lambda : sense(self, robot)
            }

        methods.update(shared_methods)

        robot.animate(self.code[team.value], methods, debug=self.debug)

        if robot_type == RobotType.PAWN:
            self.queue[self.robot_count] = robot
            self.robots[row][col] = robot
        else:
            self.lords.append(robot)

        self.robot_count += 1

    def on_the_map(self, row, col):
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return True
        return False
    
    def flood_fill(self, robot_loc, tower_loc):
        queue = [robot_loc]
        visited = set()


        cardinal_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
        while queue:
            loc = queue.pop(0)
            if loc.equals(tower_loc):
                return True

            if loc in visited or self.paint[loc.x][loc.y] != robot_loc.team:
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


    #### DEBUG METHODS: NOT AVAILABLE DURING CONTEST ####

    def view_board(self, colors=True):
        """
        @DEBUG_METHOD
        THIS METHOD IS NOT AVAILABLE DURING ACTUAL GAMES.

        Helper method that displays the full board as a human-readable string.
        """
        board = ''
        for i in range(self.board_size):
            for j in range(self.board_size):
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
        origin = self.origin
        width = self.board_width
        height = self.board_height
        ceiled_radius = math.ceil(math.sqrt(radius_squared)) + 1 # add +1 just to be safe
        minX = max(center.x - ceiled_radius, 0)
        minY = max(center.y - ceiled_radius, 0)
        maxX = min(center.x + ceiled_radius, width - 1)
        maxY = min(center.y + ceiled_radius, height - 1)

        for x in range(minX, maxX+1):
            for y in range(minY+1):
                new_location = MapLocation(x, y) 
                if (center.is_within_distance_squared(new_location, radius_squared)):
                    return_locations.append(new_location)
        return return_locations
      
    def mark_location(self, team, loc, color):
        self.markers[team][loc.x][loc.y] = color
    
    def is_passable(self, loc):
        return not self.walls[loc.x][loc.y] and self.robots[loc.x][loc.y] == None

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass

class GameError(Exception):
    """Raised for errors that arise within the Game"""
    pass
