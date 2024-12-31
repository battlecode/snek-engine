from .direction import Direction

class MapLocation:

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def compare_to(self, other):
        if self.x != other.x:
            return self.x - other.x
        return self.y - other.y
    
    def equals(self, other):
        if not isinstance(other, MapLocation):
            return False
        return self.x == other.x and self.y == other.y
    
    def to_string(self):
        return (self.x, self.y)

    def distance_squared_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return dx*dx + dy*dy
    
    def is_within_distance_squared(self, other, distance_squared):
        return self.distance_squared_to(other) <= distance_squared
    
    def is_adjacent_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return -1 <= dx <= 1 and -1 <= dy <= 1
    
    def direction_to(self, other):
        if other is None:
            return None
        
        dx = other.x - self.x
        dy = other.y - self.y

        if abs(dx) >= 2.414*abs(dy):
            return Direction.EAST if dx > 0 else Direction.WEST if dx < 0 else Direction.CENTER
        
        elif abs(dy) >= 2.414*abs(dx):
            return Direction.NORTH if dy > 0 else Direction.SOUTH

        else:
            if dx > 0 and dy > 0:
                return Direction.NORTHEAST
            elif dx > 0 and dy < 0:
                return Direction.SOUTHEAST
            elif dx < 0 and dy > 0:
                return Direction.NORTHWEST
            elif dx < 0 and dy < 0:
                return Direction.SOUTHWEST

    def translate(self, dx, dy):
        return MapLocation(self.x + dx, self.y + dy)

    def add(self, dir):
        return self.translate(dir.value[0], dir.value[1])
    
    def subtract(self, dir):
        return self.translate(-dir.value[0], -dir.value[1])
    
    def __str__(self):
        return f'({self.x}, {self.y})'
