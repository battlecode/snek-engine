from enum import Enum


class Team(Enum):
    WHITE = 0
    BLACK = 1

    def opponent(self):
        if self == Team.WHITE:
            return Team.BLACK
        else:
            return Team.WHITE