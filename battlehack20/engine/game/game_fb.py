import flatbuffers
from enum import Enum
from .constants import GameConstants
from .robot_type import RobotType
import fb_schema.TeamData as TeamData
import fb_schema.GameHeader as GameHeader
import fb_schema.EventWrapper as EventWrapper
import fb_schema.Event as Event
import fb_schema.GameFooter as GameFooter
import fb_schema.Vec as Vec
import fb_schema.RobotTypeMetadata as RobotTypeMetadata
from .fb_helpers import *

class GameFB:

    class State(Enum):
        GAME_HEADER = 0,
        IN_GAME = 1,
        IN_MATCH = 2,
        DONE = 3

    def __init__(self, game_info):
        self.builder = flatbuffers.Builder(1024)
        self.state = self.State.GAME_HEADER
        self.game_info = game_info
        self.events = []
    
        self.team_ids = []
        self.team_money = []
        self.turns = []
        self.died_ids = []
        self.current_round = []
        self.logger = []
        self.current_actions = []
        self.current_action_types = []
        self.current_map_width = 0

    def make_game_header(self):
        self.state = self.State.IN_GAME

        spec_version_offset = self.builder.CreateString(GameConstants.SPEC_VERSION)

        name = self.builder.CreateString(self.game_info.team_a_name)
        package_name = self.builder.CreateString(self.game_info.team_a_package)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, team_to_fb_id(Team.A))
        team_a_offset = TeamData.End()

        name = self.builder.CreateString(self.game_info.team_b_name)
        package_name = self.builder.CreateString(self.game_info.team_b_package)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, team_to_fb_id(Team.B))
        team_b_offset = TeamData.End(self.builder)

        teams_offset = create_vector(self.builder, GameHeader.StartTeamsVector, [team_a_offset, team_b_offset])
        robot_type_metadata_offset = self.make_robot_type_metadata()

        GameHeader.Start(self.builder)
        GameHeader.AddSpecVersion(self.builder, spec_version_offset)
        GameHeader.AddTeams(self.builder, teams_offset)
        GameHeader.AddRobotTypeMetadata(robot_type_metadata_offset)
        game_header_offset = GameHeader.End(self.builder)

        #TODO serialize GameConstants
        EventWrapper.Start(self.builder)
        EventWrapper.AddEType(self.builder, Event.Event().GameHeader)
        EventWrapper.AddE(game_header_offset)
        event_wrapper_offset = EventWrapper.End(self.builder)
        self.events.append(event_wrapper_offset)

    def make_game_footer(self, winner):
        self.state = self.State.DONE

        GameFooter.Start(self.builder)
        GameFooter.AddWinner(self.builder, winner.value)
        game_footer_offset = GameFooter.End(self.builder)
        
        EventWrapper.Start(self.builder)
        EventWrapper.AddEType(self.builder, Event.Event().GameFooter)
        EventWrapper.AddE(self.builder, game_footer_offset)
        EventWrapper.AddE()

    def make_game_constants(self):
        pass

    def make_robot_type_metadata(self):
        offsets = []
        for robot_type in RobotType:
            level_1_type = robot_type_from_fb(fb_from_robot_type(robot_type))
            if level_1_type != robot_type:
                continue
            RobotTypeMetadata.Start(self.builder)
            RobotTypeMetadata.AddType(self.builder, fb_from_robot_type(robot_type))
            RobotTypeMetadata.AddActionCooldown(self.builder, robot_type.action_cooldown)
            RobotTypeMetadata.AddActionRadiusSquared(self.builder, robot_type.action_radius_squared)
            RobotTypeMetadata.AddBaseHealth(self.builder, robot_type.health)
            RobotTypeMetadata.AddBytecodeLimit(self.builder, 1000) #TODO :skull:
            RobotTypeMetadata.AddMovementCooldown(self.builder, GameConstants.MOVEMENT_COOLDOWN)
            RobotTypeMetadata.AddVisionRadiusSquared(self.builder, GameConstants.VISION_RADIUS_SQUARED)
            offsets.append(RobotTypeMetadata.End(self.builder))
        return create_vector(self.builder, GameHeader.StartRobotTypeMetadataVector, offsets)

    #Single match serialization methods

    def make_match_header(self):
        self.state = self.State.IN_MATCH
        #should make gamemapio before doing this


    def make_match_footer(self):
        pass

    def start_round(self, round_num):
        pass

    def end_round(self):
        pass

    def start_round(self):
        pass

    def end_round(self):
        pass

    def start_turn(self, robot_id):
        pass

    def end_turn(self, robot_id):
        pass

    def add_damage_action(self, damaged_robot_id, loc):
        return 

    def add_paint_action(self, loc):
        pass

    # helper methods