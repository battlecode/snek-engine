class MapInfo:
    def __init__(self, loc, passable, ruins, tower, paint_color, territory, tower_type):
        self.loc = loc
        self.passable = passable
        self.ruins = ruins
        self.tower = tower
        self.paint_color = paint_color
        self.tower_type = tower_type
    

    def isPassable(self): 
        return self.passable
    
    def isRuins(self): 
        return self.ruins
    

    def isTower(self): 
        return self.tower
    
    def getPaintColor(self):
        return self.paint_color
    

    def getTowerType(self):
        return self.tower_type
    
    def getLocation(self):
        return self.loc


    def __str__(self):
        return f"Location: {self.loc} \n \
            isPassable: {self.isPassable} \n \
            isRuins: {self.isRuins} \n \
            isTower: {self.isTower} \n  \
            paintColor: {self.paint_color}"


    
