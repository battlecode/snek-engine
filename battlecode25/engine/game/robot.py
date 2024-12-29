from __future__ import annotations
from ..container.runner import RobotRunner
from .robot_type import RobotType
from .map_location import MapLocation
from .constants import GameConstants
from .team import Team
from .robot_info import RobotInfo

#Imported for type checking
if 1 == 0:
    from .game import Game

class Robot:

    def __init__(self, game: Game, id, team: Team, type: RobotType, loc: MapLocation, send_spawn_action=True):
        self.game = game
        self.id = id
        self.team = team
        self.type = type
        self.loc = loc
        self.died_loc = None
        self.health = self.type.health
        self.paint = self.type.paint_capacity // 2
        self.bytecode_limit = GameConstants.BYTECODE_LIMIT
        self.bytecodes_used = 0
        self.rounds_alive = 0
        self.action_cooldown = type.action_cooldown
        self.movement_cooldown = GameConstants.COOLDOWN_LIMIT
        self.indicator_string = ""
        self.runner = None
        self.debug = False
        self.logs = []
        self.send_spawn_action = send_spawn_action

    def add_paint(self, amount): 
        new_amount = self.paint + amount
        self.paint = max(0, min(new_amount, self.type.paint_capacity))

    def add_health(self, amount):
        self.health += amount
        self.health = min(self.health, self.type.health)
        if self.health <= 0:
            self.game.destroy_robot(self.id)

    def calc_paint_cooldown_multiplier(self):
        paint_percent = self.paint / self.type.paint_capacity
        if paint_percent < 0.5:
            return 2 - 2 * paint_percent
        return 0
    
    def add_action_cooldown(self):
        self.action_cooldown += self.type.action_cooldown * self.calc_paint_cooldown_multiplier()
    
    def add_movement_cooldown(self):
        self.movement_cooldown += round(GameConstants.MOVEMENT_COOLDOWN * self.calc_paint_cooldown_multiplier())

    def log(self, msg):
        self.logs.append(msg)

    def error(self, msg):
        self.logs.append(msg)

    def animate(self, code, methods, debug=False):
        self.runner = RobotRunner(code, methods, self.log, self.error, debug=debug)
        self.debug = debug

    def turn(self):
        self.process_beginning_of_turn()
        self.logs.clear()
        self.runner.run()
        for log in self.logs:
            print(log)
        self.process_end_of_turn()

    def process_beginning_of_round(self):
        self.indicator_string = ""
        self.died_loc = None
        self.add_paint(self.type.paint_per_turn)
        self.game.team_info.add_coins(self.team, self.type.money_per_turn)

    def process_beginning_of_turn(self):
        self.action_cooldown
        self.action_cooldown = max(0, self.action_cooldown - GameConstants.COOLDOWNS_PER_TURN)
        self.movement_cooldown = max(0, self.movement_cooldown - GameConstants.COOLDOWNS_PER_TURN)
        self.game.game_fb.start_turn(self.id)
        if self.send_spawn_action:
            self.game.game_fb.add_spawn_action(self.loc, self.team, self.type)
            self.send_spawn_action = False
    
    def process_end_of_turn(self):
        loc_idx = self.game.loc_to_index(self.loc)
        paint_status = self.game.paint[loc_idx]

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

        self.game.game_fb.end_turn(self.id, self.health, self.paint, self.movement_cooldown, self.action_cooldown, self.bytecodes_used, self.loc)
        self.rounds_alive += 1

    def get_robot_info(self) -> RobotInfo:
        return RobotInfo(self.id, self.team, self.type, self.health, self.loc, self.paint)

    def __str__(self):
        team = 'A' if self.team == Team.A else "B"
        return '%s%3d' % (team, self.id)
