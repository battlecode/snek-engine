import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p1', help="Path to a folder containing a bot.py file.")
    parser.add_argument('--p2', help="Path to a folder containing a bot.py file.")
    parser.add_argument('--map', help="Path to a map file.")
    parser.add_argument('--show_indicators', default='false', choices=('true', 'false'), help="Show debug indicators in output file")
    args = parser.parse_args()
    
    from battlecode25 import run_game, RunGameArgs

    print(f"Playing game between {args.p1} and {args.p2} on {args.map}")

    # Run the game
    # TODO: look for builtin maps
    game_args = RunGameArgs(
        player1_dir=f"players/{args.p1}",
        player2_dir=f"players/{args.p2}",
        map_path=f"maps/{args.map}.map25",
        out_dir="matches",
        show_indicators=True,
        debug=True  # TODO: debug option
    )
    run_game(game_args)
