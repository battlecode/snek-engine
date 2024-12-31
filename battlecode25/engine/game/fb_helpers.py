from .robot_type import RobotType
from ..schema import VecTable
from ..schema import WinType
from ..schema import EventWrapper
from .team import Team
import flatbuffers
from .domination_factor import DominationFactor

def robot_type_from_fb(b: int) -> RobotType:
    unit_type_mapping = {
        1: RobotType.LEVEL_ONE_PAINT_TOWER,
        2: RobotType.LEVEL_ONE_MONEY_TOWER,
        3: RobotType.LEVEL_ONE_DEFENSE_TOWER,
        4: RobotType.SOLDIER,
        5: RobotType.SPLASHER,
        6: RobotType.MOPPER,
        0: RobotType.LEVEL_ONE_PAINT_TOWER  # TODO: fix
    }
    if b in unit_type_mapping:
        return unit_type_mapping[b]
    raise RuntimeError(f"No unit type for {b}")

def fb_from_robot_type(unit_type: RobotType) -> int:
    if unit_type in {
        RobotType.LEVEL_ONE_PAINT_TOWER,
        RobotType.LEVEL_TWO_PAINT_TOWER,
        RobotType.LEVEL_THREE_PAINT_TOWER
    }:
        return 1
    elif unit_type in {
        RobotType.LEVEL_ONE_MONEY_TOWER,
        RobotType.LEVEL_TWO_MONEY_TOWER,
        RobotType.LEVEL_THREE_MONEY_TOWER
    }:
        return 2
    elif unit_type in {
        RobotType.LEVEL_ONE_DEFENSE_TOWER,
        RobotType.LEVEL_TWO_DEFENSE_TOWER,
        RobotType.LEVEL_THREE_DEFENSE_TOWER
    }:
        return 3
    elif unit_type == RobotType.SOLDIER:
        return 4
    elif unit_type == RobotType.SPLASHER:
        return 5
    elif unit_type == RobotType.MOPPER:
        return 6
    else:
        raise RuntimeError(f"Cannot find byte encoding for {unit_type}")
    
def fb_from_domination_factor(factor):
    match factor:
        case DominationFactor.PAINT_ENOUGH_AREA:
            return WinType.WinType().MAJORITY_PAINTED
        case DominationFactor.MORE_SQUARES_PAINTED:
            return WinType.WinType().AREA_PAINTED
        case DominationFactor.MORE_TOWERS_ALIVE:
            return WinType.WinType().MORE_TOWERS
        case DominationFactor.MORE_MONEY:
            return WinType.WinType().MORE_MONEY
        case DominationFactor.MORE_PAINT_IN_UNITS:
            return WinType.WinType().MORE_STORED_PAINT
        case DominationFactor.MORE_ROBOTS_ALIVE:
            return WinType.WinType().MORE_ROBOTS
        case DominationFactor.WON_BY_DUBIOUS_REASONS:
            return WinType.WinType().COIN_FLIP
        case DominationFactor.RESIGNATION:
            return WinType.WinType().RESIGNATION
        case _:
            return None  # Default case
        
def fb_from_die_type(was_exception):
    return 1 if was_exception else 0
    
def fb_from_team(team):
    if team == Team.A: return 1
    elif team == Team.B: return 2
    return 0

def team_from_fb(team):
    if team == 1: return Team.A
    elif team == 2: return Team.B
    return Team.NEUTRAL

def fb_from_paint_type(is_secondary):
    return 1 if is_secondary else 0

def int_rgb(red, green, blue):
    return (red << 16) + (green << 8) + blue
    
def create_vector(builder: flatbuffers.Builder, create_func, data, append_func=None):
    if append_func == None:
        append_func = builder.PrependUOffsetTRelative
    create_func(builder, len(data))
    for d in reversed(data):
        append_func(d)
    return builder.EndVector()

def create_vec_table(builder: flatbuffers.Builder, xs, ys):
    assert len(xs) == len(ys), "Vec table must have the same number of x and y values"
    xs_offset = create_vector(builder, VecTable.StartXsVector, xs, builder.PrependInt32)
    ys_offset = create_vector(builder, VecTable.StartYsVector, ys, builder.PrependInt32)
    VecTable.Start(builder)
    VecTable.AddXs(builder, xs_offset)
    VecTable.AddYs(builder, ys_offset)
    return VecTable.End(builder)

def create_event_wrapper(builder, type, event_offset):
    EventWrapper.Start(builder)
    EventWrapper.AddEType(builder, type)
    EventWrapper.AddE(builder, event_offset)
    return EventWrapper.End(builder)
