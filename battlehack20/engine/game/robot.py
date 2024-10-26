from ..container.runner import RobotRunner
from .robottype import RobotType
from .map_location import MapLocation
from .constants import GameConstants

class Robot:
    STARTING_HEALTH = 1
    STARTING_PAINT = 0

    def __init__(self, x, y, team, id, type=RobotType.PAWN):
        self.id = id
        self.type = type
        self.loc = MapLocation(x, y)
        self.has_moved = False
        self.spawned = True
        self.movement_cooldown = GameConstants.COOLDOWN_LIMIT

        if self.type == RobotType.SOLDIER:
            self.health = 250
            self.max_paint = 200
            self.paint = 100 
            self.attack_range_squared = 20
        elif self.type == RobotType.SPLASHER:
            self.health = 150
            self.max_paint = 300
            self.paint = 150
            self.attack_range_squared = 9
        elif self.type == RobotType.MOPPER:
            self.health = 50
            self.max_paint = 100
            self.paint = 50
            self.attack_range_squared = 4
        elif self.type == RobotType.TOWER:
            self.health = 500
            self.max_paint = 0
            self.paint = 0
            self.single_attack_range_squared = 1
            self.aoe_attack_range_squared = 4 
        else:
            self.healt = Robot.STARTING_HEALTH
            self.paint = Robot.STARTING_PAINT
            self.max_paint = Robot.STARTING_PAINT
        
        self.logs = []
        self.team = team

        self.runner = None
        self.debug = False
    
    def add_paint(self, amount):
        """Increase paint, but not exceeding max_paint."""
        if amount < 0:
            raise ValueError("Cannot add a negative amount of paint.")
        self.paint = min(self.paint + amount, self.max_paint)

    def use_paint(self, amount):
        """Use paint, ensuring enough paint is available."""
        if amount > self.paint:
            raise RuntimeError("Not enough paint to perform this action.")
        self.paint -= amount


    def get_location(self):
        return self.loc

    def animate(self, code, methods, debug=False):
        self.runner = RobotRunner(code, methods, self.log, self.error, debug=debug)
        self.debug = debug

    def kill(self):
        self.runner.kill()

    def log(self, msg):
        if not isinstance(msg, str):
            raise RuntimeError('Can only log strings.')

        self.logs.append({'type': 'log', 'msg': msg})

        if self.debug:
            if self.type == RobotType.OVERLORD:
                print(f'[Robot {self.id} log]', msg)
            else:
                team = 'BLACK' if self.team.value else 'WHITE'
                print(f'[Robot {self.id} {team} log]', msg)

    def error(self, msg):
        if not isinstance(msg, str):
            raise RuntimeError('Can only error strings.')

        self.logs.append({'type': 'error', 'msg': msg})

        if self.debug:
            if self.type == RobotType.OVERLORD:
                print(f'\u001b[31m[Robot {self.id} error]\u001b[0m', msg)
            else:
                team = 'BLACK' if self.team.value else 'WHITE'
                print(f'\u001b[31m[Robot {self.id} {team} error]\u001b[0m', msg)

    def turn(self):
        self.logs.clear()
        self.has_moved = False

        self.runner.run()

    def __str__(self):
        team = 'B' if self.team.value else 'W'
        return '%s%3d' % (team, self.id)

    def __repr__(self):
        team = 'BLACK' if self.team.value else 'WHITE'
        return f'<ROBOT {self.id} {team}>'
