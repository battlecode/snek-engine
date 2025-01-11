import flatbuffers
from enum import Enum
from .constants import GameConstants
from .unit_type import UnitType
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
from ..schema import SplashAction
from .fb_helpers import *
from .map_fb import serialize_map
from pathlib import Path
from .websocket_server import WebSocketServer
from .initial_map import InitialMap
import gzip
import io

class GameFB:

    class State(Enum):
        GAME_HEADER = 0,
        IN_GAME = 1,
        IN_MATCH = 2,
        DONE = 3

    def __init__(self, game_args, websocket_server: WebSocketServer):
        self.file_builder = flatbuffers.Builder(1024)
        self.packet_builder = None
        if websocket_server:
            self.packet_builder = flatbuffers.Builder(1024)
        self.websocket_server = websocket_server
        self.state = self.State.GAME_HEADER
        self.game_args = game_args
        self.show_indicators = game_args.show_indicators
        self.events = []
        self.match_headers = []
        self.match_footers = []

        self.initial_map = None
        self.team_ids = []
        self.team_money = []
        self.team_coverage = []
        self.team_resource_patterns = []
        self.turns = [[], []]
        self.died_ids = []
        self.current_round = 0
        self.logger = []
        self.timeline_markers = [[], []]
        self.current_actions = [[], []]
        self.current_action_types = [[], []]

    def for_all_builders(self, func):
        func(self.file_builder, 0)
        if self.packet_builder:
            func(self.packet_builder, 1)

    def for_all_builders_handle_event(self, func):
        event_offset = func(self.file_builder, 0)
        self.events.append(event_offset)
        if self.packet_builder:
            event_offset = func(self.packet_builder, 1)
            self.packet_builder.Finish(event_offset)
            buf = self.packet_builder.Output()
            self.websocket_server.add_message_to_queue(buf)

    def make_game_header(self):
        self.state = self.State.IN_GAME

        def write_game_header(builder, idx):
            spec_version_offset = builder.CreateString(GameConstants.SPEC_VERSION)

            p1_name = Path(self.game_args.player1_dir).name
            p2_name = Path(self.game_args.player2_dir).name

            name = builder.CreateString(self.game_args.player1_name)
            package_name = builder.CreateString(p1_name)
            TeamData.Start(builder)
            TeamData.AddName(builder, name)
            TeamData.AddPackageName(builder, package_name)
            TeamData.AddTeamId(builder, fb_from_team(Team.A))
            team_a_offset = TeamData.End(builder)

            name = builder.CreateString(self.game_args.player2_name)
            package_name = builder.CreateString(p2_name)
            TeamData.Start(builder)
            TeamData.AddName(builder, name)
            TeamData.AddPackageName(builder, package_name)
            TeamData.AddTeamId(builder, fb_from_team(Team.B))
            team_b_offset = TeamData.End(builder)

            teams_offset = create_vector(builder, GameHeader.StartTeamsVector, [team_a_offset, team_b_offset])
            robot_type_metadata_offset = self.make_robot_type_metadata(builder)

            GameplayConstants.Start(builder)
            gameplay_constants_offset = GameplayConstants.End(builder)

            GameHeader.Start(builder)
            GameHeader.AddSpecVersion(builder, spec_version_offset)
            GameHeader.AddTeams(builder, teams_offset)
            GameHeader.AddConstants(builder, gameplay_constants_offset)
            GameHeader.AddRobotTypeMetadata(builder, robot_type_metadata_offset)
            game_header_offset = GameHeader.End(builder)
            
            return create_event_wrapper(builder, Event.Event().GameHeader, game_header_offset)
        self.for_all_builders_handle_event(write_game_header)

    def make_game_footer(self, winner):
        self.state = self.State.DONE
        def write_game_footer(builder, idx):
            GameFooter.Start(builder)
            GameFooter.AddWinner(builder, fb_from_team(winner))
            game_footer_offset = GameFooter.End(builder)
            return create_event_wrapper(builder, Event.Event().GameFooter, game_footer_offset)
        self.for_all_builders_handle_event(write_game_footer)

    def finish_and_save(self, path):
        assert self.state == self.State.DONE, "Can't write unfinished game"
        events_offset = create_vector(self.file_builder, GameWrapper.StartEventsVector, self.events)
        match_headers_offset = create_vector(self.file_builder, GameWrapper.StartMatchHeadersVector, self.match_headers)
        match_footers_offset = create_vector(self.file_builder, GameWrapper.StartMatchFootersVector, self.match_footers)
        GameWrapper.Start(self.file_builder)
        GameWrapper.AddEvents(self.file_builder, events_offset)
        GameWrapper.AddMatchHeaders(self.file_builder, match_headers_offset)
        GameWrapper.AddMatchFooters(self.file_builder, match_footers_offset)
        game_wrapper_offset = GameWrapper.End(self.file_builder)
        self.file_builder.Finish(game_wrapper_offset)
        buf = self.file_builder.Output()
        with gzip.open(path, "wb") as file:
            file.write(buf)

    def make_game_constants(self):
        pass

    def make_robot_type_metadata(self, builder):
        offsets = []
        for robot_type in UnitType:
            level_1_type = robot_type_from_fb(fb_from_robot_type(robot_type))
            if level_1_type != robot_type:
                continue
            RobotTypeMetadata.Start(builder)
            RobotTypeMetadata.AddType(builder, fb_from_robot_type(robot_type))
            RobotTypeMetadata.AddActionCooldown(builder, robot_type.action_cooldown)
            RobotTypeMetadata.AddActionRadiusSquared(builder, robot_type.action_radius_squared)
            RobotTypeMetadata.AddBaseHealth(builder, robot_type.health)
            bytecode_limit = GameConstants.ROBOT_BYTECODE_LIMIT if robot_type.is_robot_type() else GameConstants.TOWER_BYTECODE_LIMIT
            RobotTypeMetadata.AddBytecodeLimit(builder, bytecode_limit)
            RobotTypeMetadata.AddMovementCooldown(builder, GameConstants.MOVEMENT_COOLDOWN)
            RobotTypeMetadata.AddVisionRadiusSquared(builder, GameConstants.VISION_RADIUS_SQUARED)
            if robot_type.is_robot_type():
                base_paint = round(robot_type.paint_capacity * GameConstants.INITIAL_ROBOT_PAINT_PERCENTAGE / 100)
            else:
                base_paint = GameConstants.INITIAL_TOWER_PAINT_AMOUNT
            RobotTypeMetadata.AddBasePaint(builder, base_paint)
            RobotTypeMetadata.AddMaxPaint(builder, robot_type.paint_capacity)
            RobotTypeMetadata.AddMessageRadiusSquared(builder, GameConstants.MESSAGE_RADIUS_SQUARED)
            offsets.append(RobotTypeMetadata.End(builder))
        return create_vector(builder, GameHeader.StartRobotTypeMetadataVector, offsets)

    #Single match serialization methods

    def make_match_header(self, initial_map: InitialMap):
        self.state = self.State.IN_MATCH
        def write_match_header(builder, idx):
            map_offset = serialize_map(builder, initial_map)
            self.initial_map = initial_map

            MatchHeader.Start(builder)
            MatchHeader.AddMap(builder, map_offset)
            MatchHeader.AddMaxRounds(builder, initial_map.rounds)
            match_header_offset = MatchHeader.End(builder)
            return create_event_wrapper(builder, Event.Event().MatchHeader, match_header_offset)
        
        self.for_all_builders_handle_event(write_match_header)
        self.match_headers.append(len(self.events) - 1)

    def make_match_footer(self, win_team, win_type, total_rounds):
        self.state = self.State.IN_GAME
        def write_match_footer(builder, idx):
            timeline_offset = create_vector(builder, MatchFooter.StartTimelineMarkersVector, self.timeline_markers)

            MatchFooter.Start(builder)
            MatchFooter.AddWinner(builder, fb_from_team(win_team))
            MatchFooter.AddWinType(builder, fb_from_domination_factor(win_type))
            MatchFooter.AddTotalRounds(builder, total_rounds)
            MatchFooter.AddTimelineMarkers(builder, timeline_offset)
            match_footer_offset = MatchFooter.End(builder)
            return create_event_wrapper(builder, Event.Event().MatchFooter, match_footer_offset)
        
        self.clear_match()
        self.for_all_builders_handle_event(write_match_footer)
        self.match_footers.append(len(self.events) - 1)

    def start_round(self, round_num):
        assert self.state == self.State.IN_MATCH, "Can't start a round while not in a match"
        self.current_round = round_num

    def end_round(self):
        def write_end_round(builder, idx):
            team_ids_offset = create_vector(builder, Round.StartTeamIdsVector, self.team_ids, builder.PrependInt32)
            team_money_offset = create_vector(builder, Round.StartTeamResourceAmountsVector, self.team_money, builder.PrependInt32)
            team_coverage_offset = create_vector(builder, Round.StartTeamCoverageAmountsVector, self.team_coverage, builder.PrependInt32)
            team_resource_pattern_count_offset = create_vector(builder, Round.StartTeamResourcePatternAmountsVector, self.team_resource_patterns, builder.PrependInt32)
            died_ids_offset = create_vector(builder, Round.StartDiedIdsVector, self.died_ids, builder.PrependInt32)
            turns_offset = create_vector(builder, Round.StartTurnsVector, self.turns[idx])

            Round.Start(builder)
            Round.AddTeamIds(builder, team_ids_offset)
            Round.AddTeamResourceAmounts(builder, team_money_offset)
            Round.AddTeamCoverageAmounts(builder, team_coverage_offset)
            Round.AddTeamResourcePatternAmounts(builder, team_resource_pattern_count_offset)
            Round.AddDiedIds(builder, died_ids_offset)
            Round.AddTurns(builder, turns_offset)
            Round.AddRoundId(builder, self.current_round)
            round_offset = Round.End(builder)
            return create_event_wrapper(builder, Event.Event().Round, round_offset)
        
        self.clear_round()
        self.for_all_builders_handle_event(write_end_round)

    def start_turn(self, robot_id):
        pass

    def end_turn(self, robot_id, health, paint, movement_cooldown, action_cooldown, bytecodes_used, loc):
        def write_end_turn(builder, idx):
            actions_offset = create_vector(builder, Turn.StartActionsVector, self.current_actions[idx])
            action_types_offset = create_vector(builder, Turn.StartActionsTypeVector, self.current_action_types[idx], builder.PrependByte)

            Turn.Start(builder)
            Turn.AddRobotId(builder, robot_id)
            Turn.AddActions(builder, actions_offset)
            Turn.AddActionsType(builder, action_types_offset)
            Turn.AddHealth(builder, health)
            Turn.AddPaint(builder, paint)
            Turn.AddMoveCooldown(builder, movement_cooldown)
            Turn.AddActionCooldown(builder,int(action_cooldown))
            Turn.AddBytecodesUsed(builder, bytecodes_used)
            Turn.AddX(builder, loc.x)
            Turn.AddY(builder, loc.y)
            turn_offset = Turn.End(builder)
            self.turns[idx].append(turn_offset)

        self.clear_turn()
        self.for_all_builders(write_end_turn)

    def add_damage_action(self, damaged_robot_id, damage):
        def add_action(builder, idx):
            action_offset = DamageAction.CreateDamageAction(builder, damaged_robot_id, damage)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().DamageAction)
        self.for_all_builders(add_action)

    def add_mark_action(self, loc, secondary):
        def add_action(builder, idx):
            action_offset = MarkAction.CreateMarkAction(builder, self.initial_map.loc_to_index(loc), secondary)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().MarkAction)
        self.for_all_builders(add_action)

    def add_unmark_action(self, loc):
        def add_action(builder, idx):
            action_offset = UnmarkAction.CreateUnmarkAction(builder, self.initial_map.loc_to_index(loc))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().UnmarkAction)
        self.for_all_builders(add_action)

    def add_paint_action(self, loc, is_secondary):
        def add_action(builder, idx):
            action_offset = PaintAction.CreatePaintAction(builder, self.initial_map.loc_to_index(loc), fb_from_paint_type(is_secondary))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().PaintAction)
        self.for_all_builders(add_action)

    def add_unpaint_action(self, loc):
        def add_action(builder, idx):
            action_offset = UnpaintAction.CreateUnpaintAction(builder, self.initial_map.loc_to_index(loc))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().UnpaintAction)
        self.for_all_builders(add_action)

    def add_attack_action(self, attacked_robot_id):
        def add_action(builder, idx):
            action_offset = AttackAction.CreateAttackAction(builder, attacked_robot_id)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().AttackAction)
        self.for_all_builders(add_action)

    def add_mop_action(self, id0, id1, id2):
        def add_action(builder, idx):
            action_offset = MopAction.CreateMopAction(builder, id0, id1, id2)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().MopAction)
        self.for_all_builders(add_action)

    def add_splash_action(self, loc):
        def add_action(builder, idx):
            action_offset = SplashAction.CreateSplashAction(builder, self.initial_map.loc_to_index(loc))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().SplashAction)
        self.for_all_builders(add_action)

    def add_build_action(self, tower_id):
        def add_action(builder, idx):
            action_offset = BuildAction.CreateBuildAction(builder, tower_id)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().BuildAction)
        self.for_all_builders(add_action)

    def add_transfer_action(self, other_robot_id, amount):
        def add_action(builder, idx):
            action_offset = TransferAction.CreateTransferAction(builder, other_robot_id, amount)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().TransferAction)
        self.for_all_builders(add_action)

    def add_message_action(self, reciever_id, data):
        def add_action(builder, idx):
            action_offset = MessageAction.CreateMessageAction(builder, reciever_id, data)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().MessageAction)
        self.for_all_builders(add_action)

    def add_spawn_action(self, id, loc, team, robot_type):
        def add_action(builder, idx):
            action_offset = SpawnAction.CreateSpawnAction(builder, id, loc.x, loc.y, fb_from_team(team), fb_from_robot_type(robot_type))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().SpawnAction)
        self.for_all_builders(add_action)

    def add_upgrade_action(self, tower_id, new_type: UnitType, new_health, new_paint):
        def add_action(builder, idx):
            action_offset = UpgradeAction.CreateUpgradeAction(builder, tower_id, new_health, new_type.health, new_paint, new_type.paint_capacity)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().UpgradeAction)
        self.for_all_builders(add_action)

    def add_die_action(self, id, was_exception):
        def add_action(builder, idx):
            action_offset = DieAction.CreateDieAction(builder, id, fb_from_die_type(was_exception))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().DieAction)
        self.for_all_builders(add_action)

    def add_remove_paint_action(self, affected_robot_id, paint):
        def add_action(builder, idx):
            action_offset = DamageAction.CreateDamageAction(builder, affected_robot_id, paint)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().DamageAction)
        self.for_all_builders(add_action)

    def add_complete_resource_pattern_action(self, loc):
        def add_action(builder, idx):
            action_offset = TransferAction.CreateTransferAction(builder, self.initial_map.loc_to_index(loc), 0)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().TransferAction)
        self.for_all_builders(add_action)

    def add_team_info(self, team, money_amount, coverage_amount, resource_patterns):
        self.team_ids.append(fb_from_team(team))
        self.team_money.append(money_amount)
        self.team_coverage.append(coverage_amount)
        self.team_resource_patterns.append(resource_patterns)

    def add_indicator_string(self, label):
        if not self.show_indicators:
            return
        def add_action(builder, idx):
            label_offset = builder.CreateString(label)
            IndicatorStringAction.Start(builder)
            IndicatorStringAction.AddValue(builder, label_offset)
            action_offset = IndicatorStringAction.End(builder)
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().IndicatorStringAction)
        self.for_all_builders(add_action)

    def add_indicator_dot(self, loc, red, green, blue):
        if not self.show_indicators:
            return
        def add_action(builder, idx):
            action_offset = IndicatorDotAction.CreateIndicatorDotAction(builder, self.initial_map.loc_to_index(loc), int_rgb(red, green, blue))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().IndicatorDotAction)
        self.for_all_builders(add_action)

    def add_indicator_line(self, start_loc, end_loc, red, green, blue):
        if not self.show_indicators:
            return
        def add_action(builder, idx):
            start_idx = self.initial_map.loc_to_index(start_loc)
            end_idx = self.initial_map.loc_to_index(end_loc)
            action_offset = IndicatorLineAction.CreateIndicatorLineAction(builder, start_idx, end_idx, int_rgb(red, green, blue))
            self.current_actions[idx].append(action_offset)
            self.current_action_types[idx].append(Action.Action().IndicatorLineAction)
        self.for_all_builders(add_action)

    def add_timeline_marker(self, team, label, red, green, blue):
        if not self.show_indicators:
            return
        def add_action(builder, idx):
            label_offset = builder.CreateString(label)
            TimelineMarker.Start(builder)
            TimelineMarker.AddTeam(builder, fb_from_team(team) - 1)
            TimelineMarker.AddLabel(builder, label_offset)
            TimelineMarker.AddRound(builder, self.current_round)
            TimelineMarker.AddColorHex(builder, int_rgb(red, green, blue))
            marker_offset = TimelineMarker.End(builder)
            self.timeline_markers[idx].append(marker_offset)
        self.for_all_builders(add_action)

    def add_died(self, id):
        self.died_ids.append(id)

    def clear_round(self):
        self.team_ids.clear()
        self.team_money.clear()
        self.team_coverage.clear()
        self.team_resource_patterns.clear()
        self.died_ids.clear()
        for i in range(len(self.turns)):
            self.turns[i].clear()

    def clear_turn(self):
        for i in range(len(self.current_actions)):
            self.current_actions[i].clear()
            self.current_action_types[i].clear()

    def clear_match(self):
        self.team_ids.clear()
        self.team_money.clear()
        self.died_ids.clear()
        self.current_round = 0
        self.logger.clear()
        self.timeline_markers.clear()
        for i in range(len(self.turns)):
            self.turns[i].clear()
            self.current_actions[i].clear()
            self.current_action_types[i].clear()
