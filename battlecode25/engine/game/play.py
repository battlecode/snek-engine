from dataclasses import dataclass
from pathlib import Path
import time
import os

from ..container.code_container import CodeContainer
from .team import Team
from .game_fb import GameFB
from .game import Game
from .domination_factor import DominationFactor
from . import map_fb


@dataclass
class RunGameArgs:
    player1_dir: str
    player2_dir: str
    player1_name: str  # Visual team name, not player path
    player2_name: str
    map_dir: str
    map_names: str  # Comma separated
    out_dir: str
    out_name: str | None
    show_indicators: bool
    debug: bool

def get_winner_string(args: RunGameArgs, reason: DominationFactor, team: Team, rounds: int):
    team_name = f"{args.player1_name} (A)" if team == Team.A else f"{args.player2_name} (B)"
    string = " " * ((50 - len(team_name)) // 2) + team_name + " wins (round " + str(rounds) + ")\nReason: "

    if reason == DominationFactor.PAINT_ENOUGH_AREA:
        string += "The winning team painted enough of the map."
    elif reason == DominationFactor.MORE_SQUARES_PAINTED:
        string += "The winning team won on tiebreakers (painted more of the map)."
    elif reason == DominationFactor.MORE_TOWERS_ALIVE:
        string += "The winning team won on tiebreakers (more towers alive)."
    elif reason == DominationFactor.MORE_MONEY:
        string += "The winning team won on tiebreakers (more money)"
    elif reason == DominationFactor.MORE_PAINT_IN_UNITS:
        string += "The winning team won on tiebreakers (more paint stored in units)."
    elif reason == DominationFactor.MORE_ROBOTS_ALIVE:
        string += "The winning team won on tiebreakers (more robots alive)."
    elif reason == DominationFactor.WON_BY_DUBIOUS_REASONS:
        string += "The winning team won arbitrarily (coin flip)."
    elif reason == DominationFactor.RESIGNATION:
        string += "Other team has resigned. Congrats on scaring them I guess..."
    return string

def run_game(args: RunGameArgs):
    container_a = CodeContainer.from_directory(args.player1_dir)
    container_b = CodeContainer.from_directory(args.player2_dir)
    game_fb = GameFB(args)
    game_fb.make_game_header()
    a_wins, b_wins = 0, 0

    for map_name in args.map_names.split(","):
        map_name = map_name.strip()
        initial_map = map_fb.load_map_raw(str(Path(args.map_dir) / map_name) + ".map25")
        game = Game([container_a, container_b], initial_map, game_fb, args)
        
        print("[server] -------------------- Match Starting --------------------")
        print(f"[server] {args.player1_name} vs. {args.player2_name} on {map_name}")

        game_fb.make_match_header(initial_map)
        while game.running:
            game.run_round()

        if game.winner == Team.A:
            a_wins += 1
        else:
            b_wins += 1
        game_fb.make_match_footer(game.winner, game.domination_factor, game.round)

        print("[server]", get_winner_string(args, game.domination_factor, game.winner, game.round))
        print("[server] -------------------- Match Finished --------------------")

    winner = Team.A if a_wins >= b_wins else Team.B
    game_fb.make_game_footer(winner)

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    if args.out_name:
        filename = args.out_name
    else:
        timestamp = int(time.time())
        filename = f"{args.player1_name}-vs-{args.player2_name}-on-{args.map_names}-{timestamp}.bc25"
    game_fb.finish_and_save(Path(args.out_dir) / filename)
