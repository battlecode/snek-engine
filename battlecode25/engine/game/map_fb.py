from ..schema import GameMap
from ..schema import SpawnAction
from ..schema import InitialBodyTable
from ..schema import Vec
from .fb_helpers import *
from .initial_map import MapSymmetry
from .initial_map import InitialMap
from .map_location import MapLocation
from .robot_info import RobotInfo
from .constants import GameConstants

MAP_EXTENSION = ".map25"

def serialize_map(builder: flatbuffers.Builder, initial_map: InitialMap):
    spawn_actions_offset = create_spawn_actions(builder, initial_map.initial_bodies)
    InitialBodyTable.Start(builder)
    InitialBodyTable.AddSpawnActions(builder, spawn_actions_offset)
    initial_bodies_offset = InitialBodyTable.End(builder)

    walls_offset = create_vector(builder, GameMap.StartWallsVector, initial_map.walls, builder.PrependBool)
    paint_offset = create_vector(builder, GameMap.StartPaintVector, initial_map.paint, builder.PrependByte)
    ruin_locs = [initial_map.index_to_loc(i) for i, ruin in enumerate(initial_map.ruins) if ruin]
    xs = [loc.x for loc in ruin_locs]
    ys = [loc.y for loc in ruin_locs]

    ruins_offset = create_vec_table(builder, xs, ys)
    pattern_offset = create_vector(builder, GameMap.StartPaintPatternsVector, initial_map.pattern, builder.PrependInt32)
    map_name_offset = builder.CreateString(initial_map.name)
    GameMap.Start(builder)
    GameMap.AddName(builder, map_name_offset)
    GameMap.AddSize(builder, Vec.CreateVec(builder, initial_map.width, initial_map.height))
    GameMap.AddSymmetry(builder, initial_map.symmetry.value)
    GameMap.AddRandomSeed(builder, initial_map.seed)
    GameMap.AddWalls(builder, walls_offset)
    GameMap.AddRuins(builder, ruins_offset)
    GameMap.AddInitialBodies(builder, initial_bodies_offset)
    GameMap.AddPaint(builder, paint_offset)
    GameMap.AddPaintPatterns(builder, pattern_offset)
    return GameMap.End(builder)

def deserialize_map(raw: GameMap):
    width = raw.Size().X()
    height = raw.Size().Y()
    origin = MapLocation(0, 0)
    seed = raw.RandomSeed()
    symmetry = MapSymmetry(raw.Symmetry())
    name = raw.Name()
    rounds = GameConstants.GAME_MAX_NUMBER_OF_ROUNDS
    paint = [raw.Paint(i) for i in range(raw.PaintLength())]
    walls = [raw.Walls(i) for i in range(raw.WallsLength())]
    pattern = [raw.PaintPatterns(i) for i in range(raw.PaintPatternsLength())]

    ruinsTable = raw.Ruins()
    ruins = [False] * (width * height)
    for i in range(ruinsTable.XsLength()):
        ruins[ruinsTable.Xs(i) + ruinsTable.Ys(i) * width] = True

    initial_bodies = load_spawn_actions(raw.InitialBodies())
    return InitialMap(width, height, origin, seed, rounds, name, symmetry, walls, paint, ruins, pattern, initial_bodies)

def create_spawn_actions(builder: flatbuffers.Builder, initial_bodies):
    InitialBodyTable.StartSpawnActionsVector(builder, len(initial_bodies))
    for robot in initial_bodies:
        SpawnAction.CreateSpawnAction(builder, robot.id, robot.location.x, robot.location.y, fb_from_team(robot.team), fb_from_robot_type(robot.type))
    return builder.EndVector()

def load_spawn_actions(body_table: InitialBodyTable):
    result = []
    for i in range(body_table.SpawnActionsLength()):
        spawn_action: SpawnAction.SpawnAction = body_table.SpawnActions(i)
        robot_type = robot_type_from_fb(spawn_action.RobotType())
        loc = MapLocation(spawn_action.X(), spawn_action.Y())
        initial_paint = GameConstants.INITIAL_PAINT_TOWER_PAINT if (robot_type == RobotType.LEVEL_ONE_PAINT_TOWER) else 0
        result.append(RobotInfo(i, team_from_fb(spawn_action.Team()), robot_type, robot_type.health, loc, initial_paint))
    return result

def load_map(name, path):
    full_path = path + name + MAP_EXTENSION

    with open(full_path, "rb") as file:
        return deserialize_map(GameMap.GameMap.GetRootAs(bytearray(file.read()), 0))
    
