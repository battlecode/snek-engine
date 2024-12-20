class MapInfo:

    def __init__(self, loc, passable, wall, paint, mark, ruin):
        self.loc = loc
        self.passable = passable
        self.wall = wall
        self.paint = paint
        self.mark = mark
        self.ruin = ruin

    def is_passable(self): 
        return self.passable
    
    def is_wall(self):
        return self.wall
    
    def has_ruin(self): 
        return self.ruin
    
    def get_paint(self):
        return self.paint
    
    def get_mark(self):
        return self.mark
    
    def get_map_location(self):
        return self.loc

    def __str__(self):
        return f"Location: {self.loc} \n \
            isPassable: {self.isPassable} \n \
            isRuins: {self.isRuins} \n \
            isTower: {self.isTower} \n  \
            paintColor: {self.paint_color}"