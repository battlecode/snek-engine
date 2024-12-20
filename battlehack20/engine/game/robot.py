from ..container.runner import RobotRunner
from .robot_type import RobotType
from .map_location import MapLocation
from .constants import GameConstants
from .game_fb import FBWriter

class Robot:
    STARTING_HEALTH = 1
    STARTING_PAINT = 0

    def __init__(self, game, id, team, type, loc):
        self.game = game
        self.id = id
        self.team = team
        self.type = type
        self.loc = loc
        
        self._movement_cooldown = 0
        self._action_cooldown = 0
        self.paint = self.type.paint_capacity // 2
        self.health = self.type.health

        self.runner = None
        self.debug = False
        
        self.rounds_alive = 0  
        self.match_maker = FBWriter(game)

    def add_paint(self, amount): 
        if amount < 0: 
            if -amount > self.paint: 
                raise RuntimeError("Not enough pain to perform this action")
            self.paint += amount
        else:
            self.paint = min(self.paint + amount, self.paint_capacity)
    
    def add_action_cooldown(self):
        if self.paint/self.type.paint_capacity < 0.5:
            penalty = 1 - 2 * self.paint/self.type.paint_capacity
        else:
            penalty = 0
        self._action_cooldown += self.type.action_cooldown * (1 + penalty)
    
    def add_movement_cooldown(self):
        if self.paint/self.type.paint_capacity < 0.5:
            penalty = 1 - 2 * self.paint/self.type.paint_capacity
        else:
            penalty = 0
        self._movement_cooldown += GameConstants.MOVEMENT_COOLDOWN * (1 + penalty)
    
    def get_location(self):
        return self.loc

    def animate(self, code, methods, debug=False):
        self.runner = RobotRunner(code, methods, self.log, self.error, debug=debug)
        self.debug = debug

    def kill(self):
        self.runner.kill()

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

    def process_beginning_of_round(self):
        pass

    def process_beginning_of_turn(self):
        pass
    
    def process_end_of_turn(self):
        current_location_index = self.game.loc_to_index(self.loc)
        paint_status = self.game._paint[current_location_index]

        if self.game.team_from_paint(paint_status) == self.team:
            paint_penalty = 0
        elif self.game.team_from_paint(paint_status) is None:
            paint_penalty = GameConstants.PENALTY_NEUTRAL_TERRITORY
        else:
            paint_penalty = GameConstants.PENALTY_ENEMY_TERRITORY
            adjacent_allies = [
                loc for loc in self.game.get_all_locations_within_radius_squared(self.loc, 1)
                if self.game.robots[self.game.loc_to_index(loc)] 
                and self.game.robots[self.game.loc_to_index(loc)].team == self.team
            ]
            paint_penalty += 2 * len(adjacent_allies)

        self.add_paint(-paint_penalty)

        if self.type.name == "TOWER":
            self.add_paint(self.type.paint_per_turn)
            self.game.team_info.add_coins(self.type.money_per_turn )

        self.match_maker.end_turn(self.id)
        self.rounds_alive += 1

    def __str__(self):
        team = 'B' if self.team.value else 'W'
        return '%s%3d' % (team, self.id)

    def __repr__(self):
        team = 'BLACK' if self.team.value else 'WHITE'
        return f'<ROBOT {self.id} {team}>'
