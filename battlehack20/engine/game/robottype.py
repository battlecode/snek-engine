from enum import Enum


class RobotType(Enum):
    ### (health, maximum paint stash, paint cost, chip cost, damage to towers, action cost, action cooldown, action radius (squared))
    SOLDIER = (250, 200, 100, 250, 10, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    SPLASHER = (150, 300, 150, 400, 50, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    MOPPER = (50, 100, 50, 300, 40, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    MONEY_TOWER = (0, 0, 0, 0, 0, 3, "Drawing", 100, 20, 20, 20, 10, 10, 10, 10, 15, 20, 1000, 1500, 2000)    
    PAINT_TOWER = (0, 0, 0, 0, 0, 3, "Drawing", 100, 20, 20, 20, 10, 10, 10, 5, 10, 150, 1000, 1500, 2000)
    DEFENSE_TOWER = (0, 0, 0, 0, 0, 5, "Drawing", 50, 40, 45, 50, 20, 25, 30, 0, 0, 0, 2500, 3000, 3500)

    def __init__(self, health, maximum_paint_stash, paint_cost, chip_cost, action_cooldown, action_radius_squared, pattern, pattern_update_cost,
    attack_strength_1, attack_strength_2, attack_strength_3, aoe_attack_strength_1, aoe_attack_strength_2, aoe_attack_strength_3, mining_rate_1,
    mining_rate_2, mining_rate_3, health_1, health_2, health_3): 
        self. health = health
        self.maximum_paint_stash = maximum_paint_stash
        self.paint_cost = paint_cost
        self.chip_cost = chip_cost
        self.action_cooldown = action_cooldown
        self.action_radius_squared = action_radius_squared
        self.pattern = pattern
        self.pattern_update_cost = pattern_update_cost
        self.attack_strength_1 = attack_strength_1 
        self.attack_strength_2 = attack_strength_2
        self.attack_strength_3 = attack_strength_3
        self.aoe_attack_strength_1 = aoe_attack_strength_1
        self.aoe_attack_strength_2 = aoe_attack_strength_2
        self.aoe_attack_strength_3 = aoe_attack_strength_3
        self.mining_rate_1 = mining_rate_1
        self.mining_rate_2 = mining_rate_2
        self.mining_rate_3 = mining_rate_3
        self.health_1 = health_1
        self.health_2 = health_2
        self.health_3 = health_3


    def canAttack(self): 
        return self == RobotType.SOLDIER or self == RobotType.SPLASHER
    

    def canMop(self): 
        return self == RobotType.MOPPER

    def isTower(self): 
        return self == RobotType.DEFENSE_TOWER or self == RobotType.MONEY_TOWER or self == RobotType.PAINT_TOWER

    

    
