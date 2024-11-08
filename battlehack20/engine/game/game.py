import random
from .robot import Robot
from .team import Team
from .robottype import RobotType
from .constants import GameConstants
from .robot_controller import *
import math
from .map_location import MapLocation

class Game:

    def __init__(self, code, board_width, board_height, max_rounds=GameConstants.MAX_ROUNDS, 
                 seed=GameConstants.DEFAULT_SEED, debug=False):
        random.seed(seed)

        self.code = code

        self.debug = debug
        self.running = True
        self.winner = None

        self.robot_count = 0
        self.queue = {}
        self.board_states = []
        self.lords = []

        self.board_width = board_width
        self.board_height = board_height
        self.board_size = board_width #TODO remove board_size
        self.robots = [[None] * self.board_width for _ in range(self.board_height)]
        self.paint = [[None] * self.board_width for _ in range(self.board_height)]
        self.walls = [[None] * self.board_width for _ in range(self.board_height)]
        self.round = 0
        self.max_rounds = max_rounds

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

    def check_over(self):
        winner = False

        white, black = 0, 0
        for col in range(self.board_size):
            if self.robots[0][col] and self.robots[0][col].team == Team.BLACK: black += 1
            if self.robots[self.board_size - 1][col] and self.robots[self.board_size - 1][col].team == Team.WHITE: white += 1

        if black >= (self.board_size + 1) // 2:
            winner = True

        if white >= (self.board_size + 1) // 2:
            winner = True

        if self.round > self.max_rounds:
            winner = True

        if winner:
            if white == black:
                tie = True
                for r in range(1, self.board_size):
                    if tie:
                        w, b = 0, 0
                        for c in range(self.board_size):
                            if self.robots[r][c] and self.robots[r][c].team == Team.BLACK: b += 1
                            if self.robots[self.board_size - r - 1][c] and self.robots[self.board_size - r - 1][c].team == Team.WHITE: w += 1
                        if w == b: continue
                        self.winner = Team.WHITE if w > b else Team.BLACK
                        tie = False
                if tie:
                    self.winner = random.choice([Team.WHITE, Team.BLACK])
            else:
                self.winner = Team.WHITE if white > black else Team.BLACK
            self.running = False

        if not self.running:
            self.board_states.append([row[:] for row in self.robots])
            self.process_over()

    def process_over(self):
        """
        Helper method to process once a game is finished (e.g. deleting robots)
        """
        for i in range(self.robot_count):
            if i in self.queue:
                self.delete_robot(i)


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

    def is_on_board(self, row, col):
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return True
        return False


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

    def getAllLocationsWithinRadiusSquared(self, center, radius_squared):
        """
        center: MapLocation object
        radius_squared: square of radius around center that we want locations for

        Returns a list of MapLocations within radius squared of center
        """
        returnLocations = []
        origin = self.origin
        width = self.board_width
        height = self.board_height
        ceiledRadius = math.ceil(math.sqrt(radius_squared)) + 1 # add +1 just to be safe
        minX = max(center.x - ceiledRadius, 0)
        minY = max(center.y - ceiledRadius, 0)
        maxX = min(center.x + ceiledRadius, width - 1)
        maxY = min(center.y + ceiledRadius, height - 1)

        for x in range(minX, maxX+1):
            for y in range(minY+1):
                newLocation = MapLocation(x, y) #TODO: make MapLocation class
                if (center.isWithinDistanceSquared(newLocation, radius_squared)): #TODO: make isWithinDistanceSquared method in MapLocation
                    returnLocations.append(newLocation)

class RobotError(Exception):
    """Raised for illegal robot inputs"""
    pass


class GameError(Exception):
    """Raised for errors that arise within the Game"""
    pass
