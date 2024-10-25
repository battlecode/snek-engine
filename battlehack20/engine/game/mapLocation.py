class MapLocation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    #TODO: make MapLocation class
    def getDistanceSquaredTo(self, loc):
        '''
        loc: another MapLocation

        Returns the distance squared from this map location to the other map location
        '''

        dx = (self.x - loc.x)**2
        dy = (self.y - loc.y)**2
        return dx + dy

    def isWithinDistanceSquared(self, loc, radius_squared):
        '''
        loc: another MapLocation
        radius_squared: radius squared

        Returns whether the other MapLocation is within the radius of this MapLocation 
        '''
        return self.getDistanceSquaredTo(loc) <= radius_squared
    
