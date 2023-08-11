#!/usr/bin/env python3

import sys
from time import sleep
from typing import NoReturn

from utils import *

def start_game() -> int:
    proc = Popen(['./game.py'])
    proc.communicate()
    return proc.returncode

def main() -> NoReturn:
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} TERMINAL_DEVICE')
        sys.exit(1)
    show_matrix(sys.argv[1])
    while True:
        if found_hands():
            start_game()
        sleep(1)

if __name__ == '__main__':
    main()
