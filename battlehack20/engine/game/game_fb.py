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
import fb_schema.MatchHeader as MatchHeader
import fb_schema.MatchFooter as MatchFooter
import fb_schema.Round as Round
import fb_schema.Turn as Turn
import fb_schema.DamageAction as DamageAction
import fb_schema.PaintAction as PaintAction
import fb_schema.UnpaintAction as UnpaintAction
import fb_schema.AttackAction as AttackAction
import fb_schema.MopAction as MopAction
import fb_schema.BuildAction as BuildAction
import fb_schema.TransferAction as TransferAction
import fb_schema.MessageAction as MessageAction
import fb_schema.SpawnAction as SpawnAction
import fb_schema.UpgradeAction as UpgradeAction
import fb_schema.DieExceptionAction as DieExceptionAction
import fb_schema.TimelineMarkerAction as TimelineMarkerAction
import fb_schema.IndicatorStringAction as IndicatorStringAction
import fb_schema.IndicatorDotAction as IndicatorDotAction
import fb_schema.IndicatorLineAction as IndicatorLineAction
import fb_schema.Action as Action
import fb_schema.RobotTypeMetadata as RobotTypeMetadata
from .fb_helpers import *
from .map_fb import serialize_map

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
        self.show_indicators = game_info["show_indicators"]
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
        self.current_action_types = []
        self.current_map_width = 0

    def make_game_header(self):
        self.state = self.State.IN_GAME

        spec_version_offset = self.builder.CreateString(GameConstants.SPEC_VERSION)

        name = self.builder.CreateString(self.game_info["team_a_name"])
        package_name = self.builder.CreateString(self.game_info["team_a_package"])
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, fb_from_team(Team.A))
        team_a_offset = TeamData.End()

        name = self.builder.CreateString(self.game_info["team_b_name"])
        package_name = self.builder.CreateString(self.game_info["team_b_package"])
        TeamData.Start(self.builder)
        TeamData.AddName(self.builder, name)
        TeamData.AddPackageName(self.builder, package_name)
        TeamData.AddTeamId(self.builder, fb_from_team(Team.B))
        team_b_offset = TeamData.End(self.builder)

        teams_offset = create_vector(self.builder, GameHeader.StartTeamsVector, [team_a_offset, team_b_offset])
        robot_type_metadata_offset = self.make_robot_type_metadata()

        GameHeader.Start(self.builder)
        GameHeader.AddSpecVersion(self.builder, spec_version_offset)
        GameHeader.AddTeams(self.builder, teams_offset)
        GameHeader.AddRobotTypeMetadata(robot_type_metadata_offset)
        game_header_offset = GameHeader.End(self.builder)

        #TODO serialize GameConstants
        self.events.append(create_event_wrapper(self.builder, Event.Event().GameHeader, game_header_offset))

    def make_game_footer(self, winner):
        self.state = self.State.DONE

        GameFooter.Start(self.builder)
        GameFooter.AddWinner(self.builder, fb_from_team(winner))
        game_footer_offset = GameFooter.End(self.builder)
        
        self.events.append(create_event_wrapper(self.builder, Event.Event().GameFooter, game_footer_offset))

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

    def make_match_header(self, initial_map):
        self.state = self.State.IN_MATCH
        map_offset = serialize_map(self.builder, initial_map)

        MatchHeader.Start(self.builder)
        MatchHeader.AddMap(map_offset)
        MatchHeader.AddMaxRounds(initial_map.rounds)
        match_header_offset = MatchHeader.End(self.builder)

        self.events.append(create_event_wrapper(self.builder, Event.Event().MatchHeader, match_header_offset))
        self.match_headers.append(len(self.events) - 1)

    def make_match_footer(self, win_team, win_type, total_rounds):
        MatchFooter.Start(self.builder)
        MatchFooter.AddWinner(fb_from_team(win_team))
        MatchFooter.AddWinType(fb_from_domination_factor(win_type))
        MatchFooter.AddTotalRounds(total_rounds)
        match_footer_offset = MatchFooter.End()

        self.events.append(create_event_wrapper(self.builder, Event.Event().MatchFooter, match_footer_offset))
        self.match_footers.append(len(self.events) - 1)

    def start_round(self, round_num):
        assert self.state == self.State.IN_MATCH, "Can't start a round while not in a match"
        self.current_round = round_num

    def end_round(self):
        team_ids_offset = create_vector(self.builder, Round.StartTeamIdsVector, self.team_ids)
        team_money_offset = create_vector(self.builder, Round.StartTeamResourceAmountsVector, self.team_money)
        died_ids_offset = create_vector(self.builder, Round.StartDiedIdsVector, self.died_ids)
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
        action_types_offset = create_vector(self.builder, Turn.StartActionsTypeVector, self.current_action_types)

        Turn.Start(self.builder)
        Turn.AddRobotId(self.builder, robot_id)
        Turn.AddActions(self.builder, actions_offset)
        Turn.AddActionsType(self.builder, action_types_offset)
        Turn.AddHealth(self.builder, health)
        Turn.AddPaint(self.builder, paint)
        Turn.AddMoveCooldown(self.builder, movement_cooldown)
        Turn.AddActionCooldown(self.builder, action_cooldown)
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

    def add_mop_action(self, loc):
        action_offset = MopAction.CreateMopAction(self.builder, self.initial_map.loc_to_index(loc))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().MopAction)

    def add_build_action(self, tower_id):
        action_offset = BuildAction.CreateBuildAction(self.builder, tower_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().BuildAction)

    def add_transfer_action(self, other_robot_id):
        action_offset = TransferAction.CreateTransferAction(self.builder, other_robot_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().TransferAction)

    def add_message_action(self, reciever_id, data):
        action_offset = MessageAction.CreateMessageAction(self.builder, reciever_id, data)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().MessageAction)

    def add_spawn_action(self, loc, team, robot_type):
        action_offset = SpawnAction.CreateSpawnAction(self.builder, loc.x, loc.y, fb_from_team(team), fb_from_robot_type(robot_type))
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().SpawnAction)

    def add_upgrade_action(self, tower_id):
        action_offset = UpgradeAction.CreateUpgradeAction(self.builder, tower_id)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().UpgradeAction)

    def add_die_exception_action(self):
        action_offset = DieExceptionAction.CreateDieExceptionAction(self.builder, -1)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().DieExceptionAction)

    def add_team_info(self, team, money_amount):
        self.team_ids.append(fb_from_team(team))
        self.team_money.append(money_amount)

    def add_timeline_marker(self, label):
        if not self.show_indicators:
            return
        label_offset = self.builder.CreateString(label)
        TimelineMarkerAction.Start(self.builder)
        TimelineMarkerAction.AddLabel(label_offset)
        action_offset = TimelineMarkerAction.End(self.builder)
        self.current_actions.append(action_offset)
        self.current_action_types.append(Action.Action().TimelineMarkerAction)

    def add_indicator_string(self, label):
        if not self.show_indicators:
            return
        label_offset = self.builder.CreateString(label)
        IndicatorStringAction.Start(self.builder)
        IndicatorStringAction.AddValue(label_offset)
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