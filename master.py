#!/usr/bin/env python3

from time import sleep
from typing import NoReturn

from utils import *

def start_game() -> None:
    proc = Popen(['./start_game.sh'])
    proc.communicate()

def main() -> NoReturn:
    show_matrix()
    while True:
        if found_hands():
            start_game()
        sleep(1)

if __name__ == '__main__':
    main()
