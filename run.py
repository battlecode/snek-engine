import argparse

import cProfile, pstats, io
from pstats import SortKey

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p1', required=True, help="Path to a folder containing a bot.py file.")
    parser.add_argument('--p2', required=True, help="Path to a folder containing a bot.py file.")
    parser.add_argument('--map', required=True, help="Path to a map file.")
    parser.add_argument('--show_indicators', default='false', choices=('true', 'false'), help="Show debug indicators in output file")
    args = parser.parse_args()
    
    from battlecode25 import run_game, RunGameArgs

    # Run the game
    # TODO: look for builtin maps
    game_args = RunGameArgs(
        player1_dir=f"players/{args.p1}",
        player2_dir=f"players/{args.p2}",
        player1_name=args.p1,
        player2_name=args.p2,
        map_dir="maps",
        map_names=args.map,
        out_dir="matches",
        out_name=None,
        show_indicators=True,
        debug=True,
        instrument=True
    )

    # pr = cProfile.Profile()
    # pr.enable()
    run_game(game_args)
    # pr.disable()
    # s = io.StringIO()
    # sortby = SortKey.CUMULATIVE
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())
