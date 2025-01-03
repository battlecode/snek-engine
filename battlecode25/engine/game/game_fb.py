import flatbuffers
from enum import Enum
from .constants import GameConstants
from .robot_type import RobotType
from ..schema import TeamData
from ..schema import GameHeader
from ..schema import Event
from ..schema import GameplayConstants
from ..schema import GameWrapper
from ..schema import GameFooter
from ..schema import MatchHeader
from ..schema import MatchFooter
from ..schema import Round
from ..schema import Turn
from ..schema import DamageAction
from ..schema import PaintAction
from ..schema import UnpaintAction
from ..schema import AttackAction
from ..schema import BuildAction
from ..schema import TransferAction
from ..schema import MessageAction
from ..schema import SpawnAction
from ..schema import UpgradeAction
from ..schema import DieAction
from ..schema import IndicatorStringAction
from ..schema import IndicatorDotAction
from ..schema import IndicatorLineAction
from ..schema import Action
from ..schema import RobotTypeMetadata
from ..schema import TimelineMarker
from ..schema import MopAction
from ..schema import MarkAction
from ..schema import UnmarkAction
from .fb_helpers import *
from .map_fb import serialize_map
from pathlib import Path
from .initial_map import InitialMap
import gzip
import io

class GameFB:

    class State(Enum):
        GAME_HEADER = 0,
        IN_GAME = 1,
        IN_MATCH = 2,
        DONE = 3

    def __init__(self, game_args):
        self.builder = flatbuffers.Builder(1024)
        self.state = self.State.GAME_HEADER
        self.game_args = game_args
        self.show_indicators = game_args.show_indicators
        self.events = []
        self.match_headers = []
        self.match_footers = []

        self.initial_map = []
        self.team_ids = []
        self.team_money = []
        self.turns = []
        self.died_ids = []
        self.current_round = 0
        self.logger = []
        self.current_actions = []
        self.timeline_markers = []
        self.current_action_types = []
        self.current_map_width = 0

    def make_game_header(self):
        self.state = self.State.IN_GAME

        spec_version_offset = self.builder.CreateString(GameConstants.SPEC_VERSION)

        p1_name = Path(self.game_args.player1_dir).name
        p2_name = Path(self.game_args.player2_dir).name

        name = self.builder.CreateString(self.game_args.player1_name)
        package_name = self.builder.CreateString(p1_name)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, fb_from_team(Team.A))
        team_a_offset = TeamData.End(self.builder)

        name = self.builder.CreateString(self.game_args.player2_name)
        package_name = self.builder.CreateString(p2_name)
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, fb_from_team(Team.B))
        team_b_offset = TeamData.End(self.builder)

        teams_offset = create_vector(self.builder, GameHeader.StartTeamsVector, [team_a_offset, team_b_offset])
        robot_type_metadata_offset = self.make_robot_type_metadata()

        GameplayConstants.Start(self.builder)
        gameplay_constants_offset = GameplayConstants.End(self.builder)

        GameHeader.Start(self.builder)
        GameHeader.AddSpecVersion(self.builder, spec_version_offset)
        GameHeader.AddTeams(self.builder, teams_offset)
        GameHeader.AddConstants(self.builder, gameplay_constants_offset)
        GameHeader.AddRobotTypeMetadata(self.builder, robot_type_metadata_offset)
        game_header_offset = GameHeader.End(self.builder)
        
        self.events.append(create_event_wrapper(self.builder, Event.Event().GameHeader, game_header_offset))

    def make_game_footer(self, winner):
        self.state = self.State.DONE

        GameFooter.Start(self.builder)
        GameFooter.AddWinner(self.builder, fb_from_team(winner))
        game_footer_offset = GameFooter.End(self.builder)
        
        self.events.append(create_event_wrapper(self.builder, Event.Event().GameFooter, game_footer_offset))

    def finish_and_save(self, path):
        assert self.state == self.State.DONE, "Can't write unfinished game"
        events_offset = create_vector(self.builder, GameWrapper.StartEventsVector, self.events)
        match_headers_offset = create_vector(self.builder, GameWrapper.StartMatchHeadersVector, self.match_headers)
        match_footers_offset = create_vector(self.builder, GameWrapper.StartMatchFootersVector, self.match_footers)
        GameWrapper.Start(self.builder)
        GameWrapper.AddEvents(self.builder, events_offset)
        GameWrapper.AddMatchHeaders(self.builder, match_headers_offset)
        GameWrapper.AddMatchFooters(self.builder, match_footers_offset)
        game_wrapper_offset = GameWrapper.End(self.builder)
        self.builder.Finish(game_wrapper_offset)
        buf = self.builder.Output()
        with gzip.open(path, "wb") as file:
            file.write(buf)

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
            RobotTypeMetadata.AddBytecodeLimit(self.builder, GameConstants.BYTECODE_LIMIT)
            RobotTypeMetadata.AddMovementCooldown(self.builder, GameConstants.MOVEMENT_COOLDOWN)
            RobotTypeMetadata.AddVisionRadiusSquared(self.builder, GameConstants.VISION_RADIUS_SQUARED)
            RobotTypeMetadata.AddBasePaint(self.builder, robot_type.paint_capacity // 2)
            offsets.append(RobotTypeMetadata.End(self.builder))
        return create_vector(self.builder, GameHeader.StartRobotTypeMetadataVector, offsets)

    #Single match serialization methods

    def make_match_header(self, initial_map: InitialMap):
        self.state = self.State.IN_MATCH
        map_offset = serialize_map(self.builder, initial_map)
        self.initial_map = initial_map

        MatchHeader.Start(self.builder)
        MatchHeader.AddMap(self.builder, map_offset)
        MatchHeader.AddMaxRounds(self.builder, initial_map.rounds)
        match_header_offset = MatchHeader.End(self.builder)

        self.events.append(create_event_wrapper(self.builder, Event.Event().MatchHeader, match_header_offset))
        self.match_headers.append(len(self.events) - 1)

    def make_match_footer(self, win_team, win_type, total_rounds):
        timeline_offset = create_vector(self.builder, MatchFooter.StartTimelineMarkersVector, self.timeline_markers)
        MatchFooter.Start(self.builder)
        MatchFooter.AddWinner(self.builder, fb_from_team(win_team))
        MatchFooter.AddWinType(self.builder, fb_from_domination_factor(win_type))
        MatchFooter.AddTotalRounds(self.builder, total_rounds)
        MatchFooter.AddTimelineMarkers(self.builder, timeline_offset)
        match_footer_offset = MatchFooter.End(self.builder)

        self.events.append(create_event_wrapper(self.builder, Event.Event().MatchFooter, match_footer_offset))
        self.match_footers.append(len(self.events) - 1)

    def start_round(self, round_num):
        assert self.state == self.State.IN_MATCH, "Can't start a round while not in a match"
        self.current_round = round_num

    def end_round(self):
        team_ids_offset = create_vector(self.builder, Round.StartTeamIdsVector, self.team_ids, self.builder.PrependInt32)
        team_money_offset = create_vector(self.builder, Round.StartTeamResourceAmountsVector, self.team_money, self.builder.PrependInt32)
        died_ids_offset = create_vector(self.builder, Round.StartDiedIdsVector, self.died_ids, self.builder.PrependInt32)
        turns_offset = create_vector(self.builder, Round.StartTurnsVector, self.turns)

        Round.Start(self.builder)
        Round.AddTeamIds(self.builder, team_ids_offset)
        Round.AddTeamResourceAmounts(self.builder, team_money_offset)
        Round.AddDiedIds(self.builder, died_ids_offset)
        Round.AddTurns(self.builder, turns_offset)
        Round.AddRoundId(self.builder, self.current_round)
        round_offset = Round.End(self.builder)
        self.events.append(create_event_wrapper(self.builder, Event.Event().Round, round_offset))
        self.clear_round()

    def start_turn(self, robot_id):
        pass

    def end_turn(self, robot_id, health, paint, movement_cooldown, action_cooldown, bytecodes_used, loc):
        actions_offset = create_vector(self.builder, Turn.StartActionsVector, self.current_actions)
        action_types_offset = create_vector(self.builder, Turn.StartActionsTypeVector, self.current_action_types, self.builder.PrependByte)

        Turn.Start(self.builder)
        Turn.AddRobotId(self.builder, robot_id)
        Turn.AddActions(self.builder, actions_offset)
        Turn.AddActionsType(self.builder, action_types_offset)
        Turn.AddHealth(self.builder, health)
        Turn.AddPaint(self.builder, paint)
        Turn.AddMoveCooldown(self.builder, movement_cooldown)
        Turn.AddActionCooldown(self.builder,int(action_cooldown))
        Turn.AddBytecodesUsed(self.builder, bytecodes_used)
        Turn.AddX(self.builder, loc.x)
        Turn.AddY(self.builder, loc.y)
        turn_offset = Turn.End(self.builder)
        self.turns.append(turn_offset)
        self.clear_turn()

    def add_damage_action(self, damaged_robot_id, damage):
        action_offset = DamageAction.CreateDamageAction(self.builder, damaged_robot_id, damage)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().DamageAction)

    def add_mark_action(self, loc, secondary):
        action_offset = MarkAction.CreateMarkAction(self.builder, self.initial_map.loc_to_index(loc), secondary)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().MarkAction)

    def add_unmark_action(self, loc):
        action_offset = UnmarkAction.CreateUnmarkAction(self.builder, self.initial_map.loc_to_index(loc))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().UnmarkAction)

    def add_paint_action(self, loc, is_secondary):
        action_offset = PaintAction.CreatePaintAction(self.builder, self.initial_map.loc_to_index(loc), fb_from_paint_type(is_secondary))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().PaintAction)

    def add_unpaint_action(self, loc):
        action_offset = UnpaintAction.CreateUnpaintAction(self.builder, self.initial_map.loc_to_index(loc))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().UnpaintAction)

    def add_attack_action(self, attacked_robot_id):
        action_offset = AttackAction.CreateAttackAction(self.builder, attacked_robot_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().AttackAction)

    def add_mop_action(self, id0, id1, id2):
        action_offset = MopAction.CreateMopAction(self.builder, id0, id1, id2)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().MopAction)

    def add_build_action(self, tower_id):
        action_offset = BuildAction.CreateBuildAction(self.builder, tower_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().BuildAction)

    def add_transfer_action(self, other_robot_id, amount):
        action_offset = TransferAction.CreateTransferAction(self.builder, other_robot_id, amount)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().TransferAction)

    def add_message_action(self, reciever_id, data):
        action_offset = MessageAction.CreateMessageAction(self.builder, reciever_id, data)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().MessageAction)

    def add_spawn_action(self, id, loc, team, robot_type):
        action_offset = SpawnAction.CreateSpawnAction(self.builder, id, loc.x, loc.y, fb_from_team(team), fb_from_robot_type(robot_type))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().SpawnAction)

    def add_upgrade_action(self, tower_id):
        action_offset = UpgradeAction.CreateUpgradeAction(self.builder, tower_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().UpgradeAction)

    def add_die_action(self, id, was_exception):
        action_offset = DieAction.CreateDieAction(self.builder, id, fb_from_die_type(was_exception))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().DieAction)

    def add_team_info(self, team, money_amount):
        self.team_ids.append(fb_from_team(team))
        self.team_money.append(money_amount)

    def add_indicator_string(self, label):
        if not self.show_indicators:
            return
        label_offset = self.builder.CreateString(label)
        IndicatorStringAction.Start(self.builder)
        IndicatorStringAction.AddValue(self.builder, label_offset)
        action_offset = IndicatorStringAction.End(self.builder)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().IndicatorStringAction)

    def add_indicator_dot(self, loc, red, green, blue):
        if not self.show_indicators:
            return
        action_offset = IndicatorDotAction.CreateIndicatorDotAction(self.builder, self.initial_map.loc_to_index(loc), int_rgb(red, green, blue))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().IndicatorDotAction)

    def add_indicator_line(self, start_loc, end_loc, red, green, blue):
        if not self.show_indicators:
            return
        start_idx = self.initial_map.loc_to_index(start_loc)
        end_idx = self.initial_map.loc_to_index(end_loc)
        action_offset = IndicatorLineAction.CreateIndicatorLineAction(self.builder, start_idx, end_idx, int_rgb(red, green, blue))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().IndicatorLineAction)

    def add_timeline_marker(self, team, label, red, green, blue):
        if not self.show_indicators:
            return
        label_offset = self.builder.CreateString(label)
        TimelineMarker.Start(self.builder)
        TimelineMarker.AddTeam(self.builder, fb_from_team(team))
        TimelineMarker.AddLabel(self.builder, label_offset)
        TimelineMarker.AddRound(self.builder, self.current_round)
        TimelineMarker.AddColor(self.builder, int_rgb(red, green, blue))
        marker_offset = TimelineMarker.End(self.builder)
        self.timeline_markers.append(marker_offset)

    def add_died(self, id):
        self.died_ids.append(id)

    def clear_round(self):
        self.team_ids.clear()
        self.team_money.clear()
        self.turns.clear()
        self.died_ids.clear()

    def clear_turn(self):
        self.current_actions.clear()
        self.current_action_types.clear()
