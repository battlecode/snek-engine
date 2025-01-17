from enum import Enum

class DominationFactor(Enum):
    PAINT_ENOUGH_AREA=0
    MORE_SQUARES_PAINTED=1
    MORE_TOWERS_ALIVE=2
    MORE_MONEY=3
    MORE_PAINT_IN_UNITS=4
    MORE_ROBOTS_ALIVE=5
    WON_BY_DUBIOUS_REASONS=6
    RESIGNATION=7
    DESTORY_ALL_UNITS = 8