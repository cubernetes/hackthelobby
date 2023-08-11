#!/usr/bin/env python3

import sys
from typing import NoReturn

def main() -> NoReturn:
    while True:
        chunk = sys.stdin.buffer.read(100)
        if not chunk:
            continue
        modified_chunk = chunk.replace(b'X', b'.')
        sys.stdout.buffer.write(modified_chunk)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
