#!/usr/bin/env python3

import os
from time import sleep
from typing import NoReturn

from utils import *

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def start_game() -> None:
    proc = Popen(['./start_game.sh'])
    proc.communicate()

def show_highscore() -> None:
    Popen([
        'tmux',
        'display-popup',
        '-E',
        'watch',
        '-tcn.6',
        r"""bash -c 'for _ in $(seq $(($(tput lines) / 3 - 1))); do printf "\n\033[31m"; done; printf "%$(($(tput cols) / 2 + 5))s\n" "Highscore:"; figlet -w $(tput cols) -c $(cat "/home/tosuman/42/hackthelobby/.score"); printf "\n\033[3$((RANDOM % 7 + 1))m%$(($(tput cols) / 2 + 4 + RANDOM % 8))s\n" "Show your hands!";'""",
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
