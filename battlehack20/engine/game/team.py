from enum import Enum

class Team(Enum):
    A = 0
    B = 1
    NEUTRAL = 2

    def opponent(self):
        if self == Team.A:
            return Team.B
        elif self == Team.B:
            return Team.A
        return Team.NEUTRAL