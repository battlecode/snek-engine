from enum import Enum


class RobotType(Enum):
    ### (health, maximum paint stash, paint cost, chip cost, damage to towers, action cost, action cooldown)
    SOLDIER = (250, 200, 100, 250, 20, 5, 10)
    SPLASHER = (150, 300, 150, 400, 50, 50, 50)
    MOPPER = (50, 100, 50, 300, 0, __, 40)


    def canAttack(self): 
        return self == RobotType.SOLDIER or self == RobotType.SPLASHER
    

    def canMop(self): 
        return self == RobotType.MOPPER

    

    
