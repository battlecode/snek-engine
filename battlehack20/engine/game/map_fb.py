import fb_schema.GameMap as GameMap
import fb_schema.SpawnAction as SpawnAction
import fb_schema.InitialBodyTable as InitialBodyTable
import fb_schema.Vec as Vec
from .fb_helpers import *
from .initial_map import MapSymmetry
from .initial_map import InitialMap
from .map_location import MapLocation
from .robot_info import RobotInfo
from .constants import GameConstants

MAP_EXTENSION = ".map25"

def serialize_map(builder, initial_map):
    robot_ids_offset = create_vector(builder, InitialBodyTable.StartRobotIdsVector, [robot.id for robot in initial_map.initial_bodies])
    spawn_actions_offset = create_spawn_actions(builder, initial_map.initial_bodies)
    InitialBodyTable.Start(builder)
    InitialBodyTable.AddRobotIds(builder, robot_ids_offset)
    InitialBodyTable.AddSpawnActions(spawn_actions_offset)
    initial_bodies_offset = InitialBodyTable.End(builder)

    walls_offset = create_vector(builder, GameMap.StartWallsVector, initial_map.walls)
    paint_offset = create_vector(builder, GameMap.StartPaintVector, initial_map.paint)
    ruin_locs = [initial_map.index_to_loc(i) for i, ruin in enumerate(initial_map.ruins) if ruin]
    xs = [loc.x for loc in ruin_locs]
    ys = [loc.y for loc in ruin_locs]
    ruins_offset = create_vec_table(builder, xs, ys)
    pattern_offset = create_vector(builder, GameMap.StartPaintPatternsVector, initial_map.patterns)
    GameMap.Start(builder)
    GameMap.AddName(builder, initial_map.name)
    GameMap.AddSize(builder, Vec.CreateVec(builder, initial_map.width, initial_map.height))
    GameMap.AddSymmetry(builder, initial_map.symmetry.value)
    GameMap.AddRandomSeed(builder, initial_map.seed)
    GameMap.AddWalls(builder, walls_offset)
    GameMap.AddRuins(builder, ruins_offset)
    GameMap.AddInitialBodies(builder, initial_bodies_offset)
    GameMap.AddPaint(paint_offset)
    GameMap.AddPaintPatterns(pattern_offset)
    return GameMap.End(builder)

def deserialize_map(raw: GameMap.GameMap):
    width = raw.Size().X()
    height = raw.Size().Y()
    origin = MapLocation(0, 0)
    seed = raw.RandomSeed()
    symmetry = MapSymmetry(raw.Symmetry())
    name = raw.Name()
    rounds = GameConstants.GAME_MAX_NUMBER_OF_ROUNDS
    paint = [raw.Paint(i) for i in range(raw.PaintLength())]
    walls = [raw.Walls(i) for i in range(raw.WallsLength())]
    pattern = [raw.PaintPatterns(i) for i in range(raw.PaintPatternsLength)]

    ruinsTable = raw.Ruins()
    ruins = [False] * (width * height)
    for i in range(len(ruins)):
        ruins[ruinsTable.Xs(i) + ruinsTable.Ys(i) * width] = True

    initial_bodies = load_spawn_actions(raw.InitialBodies())
    return InitialMap(width, height, origin, seed, rounds, name, symmetry, walls, paint, ruins, pattern, initial_bodies)

def create_spawn_actions(builder, initial_bodies):
    offsets = []
    for robot in initial_bodies:
        offsets.append(SpawnAction.CreateSpawnAction(builder, 
                robot.location.x, robot.location.y, fb_from_team(robot.team), fb_from_robot_type(robot.robot_type)))
    return create_vector(builder, InitialBodyTable.StartSpawnActionsVector, offsets)

def load_spawn_actions(body_table: InitialBodyTable.InitialBodyTable):
    result = []
    for i in range(body_table.RobotIdsLength()):
        spawn_action: SpawnAction.SpawnAction = body_table.SpawnActions(i)
        robot_type = robot_type_from_fb(spawn_action.RobotType())
        loc = MapLocation(spawn_action.X(), spawn_action.Y())
        result.append(RobotInfo(body_table.RobotIds(i), spawn_action.Team(), robot_type.health, loc, robot_type))
    return result

def load_map(name, path):
    full_path = path + name + MAP_EXTENSION
    try:
        with open(full_path, "rb") as file:
            return deserialize_map(GameMap.GameMap.GetRootAs(bytearray(file.read()), 0))
    except Exception as e:
        raise IOError(f"Error reading file {full_path}: {e}")
