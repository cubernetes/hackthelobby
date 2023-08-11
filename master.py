#!/usr/bin/env python3

from time import sleep
from typing import NoReturn

from utils import *

def start_game() -> None:
    proc = Popen(['./start_game.sh'])
    proc.communicate()

def show_highscore() -> None:
    Popen([
        'tmux',
        'display-popup',
        '-E',
        'watch',
        '-tcn.5',
        r"""sh -c 'for _ in $(seq $(($(tput lines) / 3))); do printf "\n\033[31m"; done; figlet -w $(tput cols) -c $(cat "/home/tosuman/42/hackthelobby/.score")'""",
    ])

def main() -> NoReturn:
    show_matrix()
    show_highscore()
    while True:
        if found_hands():
            start_game()
        sleep(1)

if __name__ == '__main__':
    main()
