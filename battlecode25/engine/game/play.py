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
    map_path: str
    out_dir: str
    show_indicators: bool
    debug: bool


def run_game(args: RunGameArgs):
    container_a = CodeContainer.from_directory(args.player1_dir)
    container_b = CodeContainer.from_directory(args.player2_dir)
    initial_map = map_fb.load_map_raw(args.map_path)
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

    p1_name = Path(args.player1_dir).name
    p2_name = Path(args.player2_dir).name
    map_name = Path(args.map_path).name.split(".bc25")[0]
    timestamp = int(time.time())
    filename = f"{p1_name}-vs-{p2_name}-on-{map_name}{timestamp}.bc25"
    game_fb.finish_and_save(Path(args.out_dir) / filename)
