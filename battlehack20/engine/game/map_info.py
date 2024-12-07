class MapInfo:
    def __init__(self, loc, passable, ruins, paint_color, robot_type):
        self.loc = loc
        self.passable = passable
        self.ruins = ruins
        self.paint_color = paint_color
        self.robot_type = robot_type
    

    def isPassable(self): 
        return self.passable
    
    def isRuins(self): 
        return self.ruins
    
    def getPaintColor(self):
        return self.paint_color
    

    def getRobotType(self):
        return self.robot_type
    
    def getLocation(self):
        return self.loc


    def __str__(self):
        return f"Location: {self.loc} \n \
            isPassable: {self.isPassable} \n \
            isRuins: {self.isRuins} \n \
            isTower: {self.isTower} \n  \
            paintColor: {self.paint_color}"


    
