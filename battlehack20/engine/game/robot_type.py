from enum import Enum


class RobotType(Enum):
    ### (health, maximum paint stash, paint cost, chip cost, damage to towers, action cost, action cooldown, action radius (squared))
    SOLDIER = (100, 250, 5, 250, -1, 200, 10, 20, 20, -1, 0, 0)
    SPLASHER = (150, 400, 50, 150, -1, 300, 50, 9, -1, 50, 0, 0)
    MOPPER = (50, 300, 0, 50, -1, 100, 30, 2, -1, -1, 0, 0)

    LEVEL_ONE_PAINT_TOWER = (0, 25, 0, 1000, 1, 1000, 10, 9, 20, 10, 5, 0)
    LEVEL_TWO_PAINT_TOWER = (0, 100, 0, 1500, 2, 1000, 10, 9, 20, 10, 10, 0)
    LEVEL_THREE_PAINT_TOWER = (0, 100, 0, 2000, 3, 1000, 10, 9, 20, 10, 15, 0)

    LEVEL_ONE_MONEY_TOWER = (0, 25, 0, 1000, 1, 1000, 10, 9, 20, 10, 0, 10)
    LEVEL_TWO_MONEY_TOWER = (0, 100, 0, 1500, 2, 1000, 10, 9, 20, 10, 0, 15)
    LEVEL_THREE_MONEY_TOWER = (0, 100, 0, 2000, 3, 1000, 10, 9, 20, 10, 0, 20)

    LEVEL_ONE_DEFENSE_TOWER = (0, 25, 0, 2500, 1, 1000, 10, 25, 60, 30, 0, 0)
    LEVEL_TWO_DEFENSE_TOWER = (0, 50, 0, 3000, 2, 1000, 10, 25, 65, 35, 0, 0)
    LEVEL_THREE_DEFENSE_TOWER = (0, 50, 0, 3500, 3, 1000, 10, 25, 70, 40, 0, 0)

    def __init__(self, paint_cost, money_cost, attack_cost, health, level, paint_capacity, action_cooldown, action_radius_squared, attack_strength, 
                 aoe_attack_strength, paint_per_turn, money_per_turn): 
        self.paint_cost = paint_cost
        self.money_cost = money_cost
        self.attack_cost = attack_cost
        self.health = health
        self.level = level
        self.paint_capacity = paint_capacity
        self.action_cooldown = action_cooldown
        self.action_radius_squared = action_radius_squared
        self.attack_strength = attack_strength
        self.aoe_attack_strength = aoe_attack_strength
        self.paint_per_turn = paint_per_turn
        self.money_per_turn = money_per_turn

    def canAttack(self): 
        return self == RobotType.SOLDIER or self == RobotType.SPLASHER
    
    def canMop(self): 
        return self == RobotType.MOPPER

    def isTower(self): 
        return not (self == RobotType.SOLDIER or self == RobotType.SPLASHER or self == RobotType.MOPPER)

    

    
