from .map_location import MapLocation
from .paint_type import PaintType
class MapInfo:

    def __init__(self, loc: MapLocation, passable: bool, wall: bool, paint: PaintType, mark: PaintType, ruin: bool, resource_pattern_center: bool):
        self.loc = loc
        self.passable = passable
        self.wall = wall
        self.paint = paint
        self.mark = mark
        self.ruin = ruin
        self.resource_pattern_center = resource_pattern_center

    def is_passable(self) -> bool: 
        return self.passable
    
    def is_wall(self) -> bool:
        return self.wall
    
    def has_ruin(self) -> bool: 
        return self.ruin
    
    def get_paint(self) -> PaintType:
        return self.paint
    
    def get_mark(self) -> PaintType:
        return self.mark
    
    def get_map_location(self) -> MapLocation:
        return self.loc
    
    def is_resource_pattern_center(self) -> bool:
        return self.resource_pattern_center

    def __str__(self):
        return f"Location: {self.loc} \n \
            passable: {self.passable} \n \
            is_wall: {self.wall} \n \
            has_ruin: {self.ruin} \n  \
            paint: {self.paint} \n \
            mark: {self.mark} \n \
            is_resource_pattern_center: {self.resource_pattern_center}\n"