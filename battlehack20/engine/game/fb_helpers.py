from .robot_type import RobotType
import fb_schema.VecTable as VecTable
import fb_schema.Vec as Vec
from .team import Team

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
    
def create_vector(builder, create_func, data):
    create_func(builder, len(data))
    for d in reversed(data):
        builder.PrependUOffsetTRelative(d)
    return builder.EndVector()

def create_vec_table(builder, xs, ys):
    assert len(xs) == len(ys), "Vec table must have the same number of x and y values"
    xs_offset = create_vector(builder, VecTable.StartXsVector, xs)
    ys_offset = create_vector(builder, VecTable.StartYsVector, ys)
    VecTable.Start(builder)
    VecTable.AddXs(xs_offset)
    VecTable.AddYs(ys_offset)
    return VecTable.End(builder)

def team_to_fb_id(builder, team):
    if team == Team.A: return 1
    elif team == Team.B: return 2
    return 0