from .team import Team
from .unit_type import UnitType
from .map_location import MapLocation

class RobotInfo:
    def __init__(self, id: int, team: Team, type: UnitType, health: int, location: MapLocation, paint_amount: int):
        self.id = id
        self.team = team
        self.type = type
        self.health = health
        self.location = location
        self.paint_amount = paint_amount
    
    def get_id(self):
        return self.id
    
    def get_team(self):
        return self.team
    
    def get_type(self):
        return self.type
    
    def get_health(self):
        return self.health
    
    def get_location(self):
        return self.location
    
    def get_paint_amount(self):
        return self.paint_amount
