import flatbuffers
from enum import Enum
from .constants import GameConstants
import fb_schema.TeamData as TeamData
import fb_schema.GameHeader as GameHeader
import fb_schema.EventWrapper as EventWrapper
import fb_schema.Event as Event
import fb_schema.GameFooter as GameFooter

class FBWriter:

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

    def make_game_header(self):
        self.state = self.State.IN_GAME

        spec_version_offset = self.builder.CreateString(GameConstants.SPEC_VERSION)

        name = self.builder.CreateString(self.game_info.team_a_name)
        package_name = self.builder.CreateString(self.game_info.team_a_package)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, 1)
        team_a_offset = TeamData.End()

        name = self.builder.CreateString(self.game_info.team_b_name)
        package_name = self.builder.CreateString(self.game_info.team_b_package)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, 1)
        team_b_offset = TeamData.End(self.builder)

        GameHeader.StartTeamsVector(self.builder, 2)
        self.builder.PrependUOffsetTRelative(team_a_offset)
        self.builder.PrependUOffsetTRelative(team_b_offset)
        teams_offset = self.builder.EndVector()

        GameHeader.Start(self.builder)
        GameHeader.AddSpecVersion(self.builder, spec_version_offset)
        GameHeader.AddTeams(self.builder, teams_offset)
        game_header_offset = GameHeader.End(self.builder)

        #TODO serialize constants and robot type data
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

    def make_robot_type_metadata(self):
        pass

    def make_match_header(self):
        pass

    def make_match_footer(self):
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