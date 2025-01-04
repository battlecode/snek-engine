from enum import Enum

dir_to_index = {
    (0, 1): 0,
    (1, 1): 1,
    (1, 0): 2,
    (1, -1): 3,
    (0, -1): 4,
    (-1, -1): 5,
    (-1, 0): 6,
    (-1, 1): 7,
    (0, 0): 8
}

class Direction(Enum):

    NORTH = (0, 1)
    NORTHEAST = (1, 1)
    EAST = (1, 0)
    SOUTHEAST = (1, -1)
    SOUTH = (0, -1)
    SOUTHWEST = (-1, -1)
    WEST = (-1, 0)
    NORTHWEST = (-1, 1)
    CENTER = (0, 0)

    def opposite(self) -> 'Direction':
        if self == Direction.CENTER:
            return self
        return dir_order[(dir_to_index[self.value] + 4) % 8]

    def rotate_left(self) -> 'Direction':
        if self == Direction.CENTER:
            return self
        return dir_order[(dir_to_index[self.value] - 1) % 8]
    
    def rotate_right(self) -> 'Direction':
        if self == Direction.CENTER:
            return self
        return dir_order[(dir_to_index[self.value] + 1) % 8]
    
    def all_directions():
        return Direction.__members__.values()
    
    def cardinal_directions():
        return [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
    
    def get_dx(self):
        return self.value[0]
    
    def get_dy(self):
        return self.value[1]
    
dir_order = [Direction.NORTH, Direction.NORTHEAST, Direction.EAST, Direction.SOUTHEAST, Direction.SOUTH, Direction.SOUTHWEST, Direction.WEST, Direction.NORTHWEST, Direction.CENTER]