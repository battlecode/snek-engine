from enum import Enum
from enum import Enum
from dataclasses import dataclass

@dataclass(frozen=True)
class RobotAttributes:
    paint_cost: int
    money_cost: int
    attack_cost: int
    health: int
    level: int
    paint_capacity: int
    action_cooldown: int
    action_radius_squared: int
    attack_strength: int
    aoe_attack_strength: int
    paint_per_turn: int
    money_per_turn: int

class UnitType(Enum):
    # Define enum members with RobotAttributes dataclass
    SOLDIER = RobotAttributes(200, 250, 5, 250, -1, 200, 10, 9, 20, -1, 0, 0)
    SPLASHER = RobotAttributes(300, 400, 50, 150, -1, 300, 50, 8, -1, 50, 0, 0)
    MOPPER = RobotAttributes(100, 300, 0, 50, -1, 100, 30, 2, -1, -1, 0, 0)

    LEVEL_ONE_PAINT_TOWER = RobotAttributes(0, 100, 0, 1000, 1, 1000, 10, 9, 20, 10, 5, 0)
    LEVEL_TWO_PAINT_TOWER = RobotAttributes(0, 250, 0, 1500, 2, 1000, 10, 9, 20, 10, 10, 0)
    LEVEL_THREE_PAINT_TOWER = RobotAttributes(0, 500, 0, 2000, 3, 1000, 10, 9, 20, 10, 15, 0)

    LEVEL_ONE_MONEY_TOWER = RobotAttributes(0, 100, 0, 1000, 1, 1000, 10, 9, 20, 10, 0, 10)
    LEVEL_TWO_MONEY_TOWER = RobotAttributes(0, 250, 0, 1500, 2, 1000, 10, 9, 20, 10, 0, 15)
    LEVEL_THREE_MONEY_TOWER = RobotAttributes(0, 500, 0, 2000, 3, 1000, 10, 9, 20, 10, 0, 20)

    LEVEL_ONE_DEFENSE_TOWER = RobotAttributes(0, 100, 0, 2500, 1, 1000, 10, 20, 60, 30, 0, 0)
    LEVEL_TWO_DEFENSE_TOWER = RobotAttributes(0, 250, 0, 3000, 2, 1000, 10, 20, 65, 35, 0, 0)
    LEVEL_THREE_DEFENSE_TOWER = RobotAttributes(0, 500, 0, 3500, 3, 1000, 10, 20, 70, 40, 0, 0)

    # Read-only property accessors for attributes
    @property
    def paint_cost(self):
        return self.value.paint_cost

    @property
    def money_cost(self):
        return self.value.money_cost

    @property
    def attack_cost(self):
        return self.value.attack_cost

    @property
    def health(self):
        return self.value.health

    @property
    def level(self):
        return self.value.level

    @property
    def paint_capacity(self):
        return self.value.paint_capacity

    @property
    def action_cooldown(self):
        return self.value.action_cooldown

    @property
    def action_radius_squared(self):
        return self.value.action_radius_squared

    @property
    def attack_strength(self):
        return self.value.attack_strength

    @property
    def aoe_attack_strength(self):
        return self.value.aoe_attack_strength

    @property
    def paint_per_turn(self):
        return self.value.paint_per_turn

    @property
    def money_per_turn(self):
        return self.value.money_per_turn

    def can_attack(self): 
        return self == UnitType.SOLDIER or self == UnitType.SPLASHER
    
    def is_robot_type(self):
        return self == UnitType.SOLDIER or self == UnitType.SPLASHER or self == UnitType.MOPPER

    def is_tower_type(self): 
        return not self.is_robot_type()
    
    def can_upgrade_type(self):
        return self.is_tower_type() and (self.level == 1 or self.level == 2)
    
    def get_next_level(self): 
        if self == UnitType.LEVEL_ONE_PAINT_TOWER:
            return UnitType.LEVEL_TWO_PAINT_TOWER
        elif self == UnitType.LEVEL_TWO_PAINT_TOWER:
            return UnitType.LEVEL_THREE_PAINT_TOWER
        
        elif self == UnitType.LEVEL_ONE_MONEY_TOWER:
            return UnitType.LEVEL_TWO_MONEY_TOWER
        elif self == UnitType.LEVEL_TWO_MONEY_TOWER:
            return UnitType.LEVEL_THREE_MONEY_TOWER
        
        elif self == UnitType.LEVEL_ONE_DEFENSE_TOWER:
            return UnitType.LEVEL_TWO_DEFENSE_TOWER
        elif self ==  UnitType.LEVEL_TWO_DEFENSE_TOWER:
            return UnitType.LEVEL_THREE_DEFENSE_TOWER