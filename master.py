#!/usr/bin/env python3

import sys
from time import sleep
from typing import NoReturn

from utils import *

def start_game() -> int:
    proc = Popen(['./start_game.sh'])
    proc.communicate()
    return proc.returncode

def main() -> NoReturn:
    show_matrix()
    while True:
        if found_hands():
            start_game()
        sleep(1)

if __name__ == '__main__':
    main()
