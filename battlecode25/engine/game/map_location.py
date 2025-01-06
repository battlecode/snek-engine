from .direction import Direction

class MapLocation:

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def compare_to(self, other: 'MapLocation') -> int:
        if self.x != other.x:
            return self.x - other.x
        return self.y - other.y

    def distance_squared_to(self, other: 'MapLocation') -> int:
        dx = self.x - other.x
        dy = self.y - other.y
        return dx*dx + dy*dy
    
    def is_within_distance_squared(self, other, distance_squared) -> bool:
        return self.distance_squared_to(other) <= distance_squared
    
    def is_adjacent_to(self, other: 'MapLocation') -> bool:
        dx = self.x - other.x
        dy = self.y - other.y
        return -1 <= dx <= 1 and -1 <= dy <= 1
    
    def direction_to(self, other: 'MapLocation') -> Direction:
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

    def translate(self, dx: int, dy: int) -> 'MapLocation':
        return MapLocation(self.x + dx, self.y + dy)

    def add(self, dir: Direction) -> 'MapLocation':
        return self.translate(dir.value[0], dir.value[1])
    
    def subtract(self, dir: Direction) -> 'MapLocation':
        return self.translate(-dir.value[0], -dir.value[1])
    
    def __hash__(self):
        return (self.y + 0x8000) & 0xffff | (self.x << 16)
    
    def __eq__(self, other: 'MapLocation'):
        return self.x == other.x and self.y == other.y
    
    def __str__(self):
        return f'({self.x}, {self.y})'
