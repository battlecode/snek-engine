import random
from .robot import Robot
from .team import Team
from .robottype import RobotType
from .constants import GameConstants
from .game import RobotError

class RobotController:

    #### SHARED METHODS ####

    def get_board_size(self):
        """
        @HQ_METHOD, @PAWN_METHOD

        Return the size of the board (int)
        """
        return self.board_size

    def get_team(self, robot):
        """
        @HQ_METHOD, @PAWN_METHOD

        Return the current robot's team (Team.WHITE or Team.BLACK)
        """
        return robot.team

    def get_type(self, robot):
        """
        @HQ_METHOD, @PAWN_METHOD

        Return the type of the unit - either RobotType.PAWN or RobotType.OVERLORD
        """
        return robot.type


    #### HQ METHODS ####

    def get_board(self):
        """
        @HQ_METHOD

        Return the current state of the board as an array of Team.WHITE, Team.BLACK, and None, representing white-occupied,
        black-occupied, and empty squares, respectively.
        """
        board = [[None] * self.board_size for _ in range(self.board_size)]

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.robots[i][j]:
                    board[i][j] = self.robots[i][j].team

        return board

    def hq_check_space(self, row, col):
        """
        @HQ_METHOD

        Checks whether a specific board space is occupied and if yes returns the team of the robot occupying the space;
        otherwise returns False. Pawns have a similar method but can only see within their sensory radius
        """
        if not self.robots[row][col]:
            return False
        return self.robots[row][col].team

    def spawn(self, robot, row, col):
        """
        @HQ_METHOD

        Spawns a pawn at the given location. Pawns can only be spawned at the edge of the board on your side of the board.
        Only the HQ can spawn units, and it can only spawn one unit per turn.
        :loc should be given as a tuple (row, col), the space to spawn on
        """
        if robot.has_moved:
            raise RobotError('you have already spawned a unit this turn')

        if (robot.team == Team.WHITE and row != 0) or (robot.team == Team.BLACK and row != self.board_size - 1):
            raise RobotError('you can only spawn in the end row of your side of the board')

        if not self.is_on_board(row, col):
            raise RobotError('you cannot spawn a unit on a space that is not on the board')

        if self.robots[row][col]:
            raise RobotError('you cannot spawn a unit on a space that is already occupied')

        self.new_robot(row, col, robot.team, RobotType.PAWN)
        robot.has_moved = True


    #### PAWN METHODS ####

    def capture(self, robot, new_row, new_col):
        """
        @PAWN_METHOD

        Diagonally capture an enemy piece.
        :new_row, new_col the position of the enemy to capture.
        Units can only capture enemy pieces that are located diagonally left or right in front of them on the board.
        """
        if robot.has_moved:
            raise RobotError('this unit has already moved this turn; robots can only move once per turn')

        row, col = robot.row, robot.col

        if self.robots[row][col] != robot:
            raise RobotError

        if not self.is_on_board(new_row, new_col):
            raise RobotError('you cannot capture a space that is not on the board')

        if not self.robots[new_row][new_col]:
            raise RobotError('you cannot capture an empty space')

        if self.robots[new_row][new_col].team == robot.team:
            raise RobotError('you cannot capture your own piece')

        if abs(col - new_col) != 1:
            raise RobotError('you must capture diagonally')

        if (robot.team == Team.WHITE and row - new_row != -1) or (robot.team == Team.BLACK and row - new_row != 1):
            raise RobotError('you must capture diagonally forwards')

        captured_robot = self.robots[new_row][new_col]

        self.delete_robot(captured_robot.id)
        self.robots[row][col] = None

        robot.row = new_row
        robot.col = new_col

        self.robots[new_row][new_col] = robot
        robot.has_moved = True

    def get_location(self, robot):
        """
        @PAWN_METHOD

        Return the current location of the robot
        """
        row, col = robot.row, robot.col
        if self.robots[row][col] != robot:
            raise RobotError('something went wrong; please contact the devs')
        return row, col

    def move_forward(self, robot):
        """
        @PAWN_METHOD

        Move the current unit forward. A unit can only be moved if there is no unit already occupying the space.
        """
        if robot.has_moved:
            raise RobotError('this unit has already moved this turn; robots can only move once per turn')

        row, col = robot.row, robot.col
        if self.robots[row][col] != robot:
            raise RobotError('something went wrong; please contact the devs')

        if robot.team == Team.WHITE:
            new_row, new_col = row + 1, col
        else:
            new_row, new_col = row - 1, col

        if not self.is_on_board(new_row, new_col):
            raise RobotError('you cannot move to a space that is not on the board')

        if self.robots[new_row][new_col]:
            raise RobotError('you cannot move to a space that is already occupied')

        self.robots[row][col] = None

        robot.row = new_row
        robot.col = new_col
        self.robots[new_row][new_col] = robot
        robot.has_moved = True

    def pawn_check_space(self, robot, row, col):
        """
        @PAWN_METHOD

        Checks whether a specific board space is occupied and if yes returns the team of the robot occupying the space;
        otherwise returns False.

        Raises a RobotError if the space is not within the sensory radius

        HQs have a similar method but can see the full board
        """
        if self.robots[robot.row][robot.col] != robot:
            raise RobotError('something went wrong; please contact the devs')

        drow, dcol = abs(robot.row - row), abs(robot.col - col)
        if max(drow, dcol) > 2:
            raise RobotError('that space is not within sensory radius of this robot')

        if not self.robots[row][col]:
            return False
        return self.robots[row][col].team

    def sense(self, robot):
        """
        @PAWN_METHOD

        Sense nearby units; returns a list of tuples of the form (row, col, robot.team) within sensor radius of this robot (excluding yourself)
        You can sense another unit other if it is within sensory radius of you; e.g. max(|robot.x - other.x|, |robot.y - other.y|) <= sensory_radius
        """
        row, col = robot.row, robot.col

        robots = []

        for i in range(-self.sensor_radius, self.sensor_radius + 1):
            for j in range(-self.sensor_radius, self.sensor_radius + 1):
                if i == 0 and j == 0:
                    continue

                new_row, new_col = row + i, col + j
                if not self.is_on_board(new_row, new_col):
                    continue

                if self.robots[new_row][new_col]:
                    robots.append((new_row, new_col, self.robots[new_row][new_col].team))

        return robots
