import time
import argparse
import faulthandler
import sys
import os
import threading
from battlecode25.engine.game.game import Game
import battlecode25.engine.game.map_fb as map_fb
from battlecode25.engine.game.game_fb import GameFB

from battlecode25 import CodeContainer, BasicViewer, GameConstants, MessageBuffer, Team

"""
This is a simple script for running bots and debugging them.

Feel free to change this script to suit your needs!

Usage:

    python3 run.py examplefuncsplayer examplefuncsplayer

        Runs examplefuncsplayer against itself. (You can omit the second argument if you want to.)

    python3 -i run.py examplefuncsplayer examplefuncsplayer

        Launches an interactive shell where you can step through the game using step().
        This is great for debugging.
    
    python3 -i run.py examplefuncsplayer exampelfuncsplayer --debug false

        Runs the script without printing logs. Instead shows the viewer in real time.

    python3 run.py -h

        Shows a help message with more advanced options.
"""

# def step(number_of_turns=1):
#     """
#     This function steps through the game the specified number of turns.

#     It prints the state of the game after every turn.
#     """

#     for i in range(number_of_turns):
#         if not game.running:
#             print(f'{game.winner} has won!')
#             break
#         game.turn()
#         viewer.view()


# def play_all(delay=0.8, keep_history=False, real_time=False):
#     """
#     This function plays the entire game, and views it in a nice animated way.

#     If played in real time, make sure that the game does not print anything.
#     """

#     if real_time:
#         viewer_poison_pill = threading.Event()
#         viewer_thread = threading.Thread(target=viewer.play_synchronized, args=(viewer_poison_pill,), kwargs={'delay': delay, 'keep_history': keep_history})
#         viewer_thread.daemon = True
#         viewer_thread.start()

#     while True:
#         if not game.running:
#             break
#         game.turn()

#     if real_time:
#         viewer_poison_pill.set()
#         viewer_thread.join()
#     else:
#         viewer.play(delay=delay, keep_history=keep_history)

#     print(f'{game.winner} wins!')

def run_game(args):
    faulthandler.enable() 
    container_a = CodeContainer.from_directory(f"players/{args.player[0]}")
    container_b = CodeContainer.from_directory(f"players/{args.player[1] if len(args.player) > 1 else args.player[0]}")
    initial_map = map_fb.load_map("DefaultSmall", "maps/")
    game_fb = GameFB(args)
    game = Game([container_a, container_b], initial_map, game_fb, args)

    #TODO support multiple matches in a game
    game_fb.make_game_header()
    game_fb.make_match_header(initial_map)
    while game.running:
        game.run_round()
    game_fb.make_match_footer(game.winner, game.domination_factor, game.round)
    game_fb.make_game_footer(game.winner)
    if not os.path.exists("matches"):
        os.mkdir("matches")
    game_fb.finish_and_save(f"./matches/{args.output}.bc25")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('player', nargs='+', help="Path to a folder containing a bot.py file.")
    parser.add_argument('--debug', default='true', choices=('true','false'), help="In debug mode (defaults to true), bot logs and additional information are displayed.")
    parser.add_argument('--max-rounds', default=GameConstants.GAME_MAX_NUMBER_OF_ROUNDS, type=int, help="Override the max number of rounds for faster games.")
    parser.add_argument('--seed', default=GameConstants.GAME_DEFAULT_SEED, type=int, help="Override the seed used for random.")
    parser.add_argument('--show_indicators', default='false', choices=('true', 'false'), help="Show debug indicators in output file")
    parser.add_argument('--output', default = 'output', help="Specify output file name")
    args = parser.parse_args()
    args.debug = args.debug == 'true'
    args.show_indicators = args.show_indicators == 'true'
    run_game(args)
