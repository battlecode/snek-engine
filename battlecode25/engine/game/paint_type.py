from enum import Enum

class PaintType(Enum):
    EMPTY = 0
    ALLY_PRIMARY = 1
    ALLY_SECONDARY = 2
    ENEMY_PRIMARY = 3
    ENEMY_SECONDARY = 4

    def is_ally(self):
        return self in {PaintType.ALLY_PRIMARY, PaintType.ALLY_SECONDARY}

    def is_primary(self):
        return self in {PaintType.ALLY_PRIMARY, PaintType.ENEMY_PRIMARY}