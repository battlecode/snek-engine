class RobotInfo:
    def __init__(self, id, team, health, location, attack_level):
        self.id = id
        self.team = team
        self.health = health
        self.location = location
        self.attack_level = attack_level
    
    def get_id(self):
        return self.id
    
    def get_team(self):
        return self.team
    
    def get_health(self):
        return self.health
    
    def get_location(self):
        return self.location
    
    def get_attack_level(self):
        return self.attack_level
    
    def get_robot_info(self, robot):
        return RobotInfo(robot.id, robot.team, robot.health, robot.location, robot.attack_level)
