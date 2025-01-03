from dataclasses import dataclass
from pathlib import Path
import time
import os

from ..container.code_container import CodeContainer
from .game_fb import GameFB
from .game import Game
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


def run_game(args: RunGameArgs):
    container_a = CodeContainer.from_directory(args.player1_dir)
    container_b = CodeContainer.from_directory(args.player2_dir)

    # TODO: Fix maps
    initial_map = map_fb.load_map_raw(str(Path(args.map_dir) / args.map_names) + ".map25")
    game_fb = GameFB(args)
    game = Game([container_a, container_b], initial_map, game_fb, args)

    #TODO support multiple matches in a game
    game_fb.make_game_header()
    game_fb.make_match_header(initial_map)
    while game.running:
        game.run_round()
    game_fb.make_match_footer(game.winner, game.domination_factor, game.round)
    game_fb.make_game_footer(game.winner)

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)

    if args.out_name:
        filename = args.out_name
    else:
        timestamp = int(time.time())
        filename = f"{args.player1_name}-vs-{args.player2_name}-on-{args.map_names}-{timestamp}.bc25"

    game_fb.finish_and_save(Path(args.out_dir) / filename)
