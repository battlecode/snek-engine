from .map_location import MapLocation
from enum import Enum

class InitialMap:

    def __init__(self, width, height, origin, seed, rounds, name, symmetry, walls, paint, ruins, pattern, initial_bodies):
        self.width = width
        self.height = height
        self.origin = origin
        self.seed = seed
        self.rounds = rounds
        self.name = name
        self.symmetry = symmetry
        self.initial_bodies = sorted(initial_bodies, key=lambda robot: robot.id)
        self.walls = walls
        self.paint = paint
        self.ruins = ruins
        self.pattern = pattern

    def index_to_loc(self, index):
        return MapLocation(index % self.width, index // self.width)
    
    def loc_to_index(self, loc):
        return loc.x + loc.y * self.width
    
class MapSymmetry(Enum):
    ROTATIONAL = 0
    HORIZONTAL = 1
    VERTICAL = 2