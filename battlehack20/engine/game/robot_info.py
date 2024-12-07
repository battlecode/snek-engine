class RobotInfo:
    def __init__(self, id, team, health, location, robot_type):
        self.id = id
        self.team = team
        self.health = health
        self.location = location
        self.robot_type = robot_type
    
    def get_id(self):
        return self.id
    
    def get_team(self):
        return self.team
    
    def get_health(self):
        return self.health
    
    def get_location(self):
        return self.location
    
    def get_robot_type(self):
        return self.robot_type
    
    
    def get_robot_info(self, robot):
        return RobotInfo(robot.id, robot.team, robot.health, robot.location, robot.attack_level)
