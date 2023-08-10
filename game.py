#!/usr/bin/env python3

import sys
from typing import NoReturn

def main() -> NoReturn:
    x = 0
    y = 0
    while True:
        chunk = sys.stdin.buffer.read(100)
        if not chunk:
            continue
        nls = chunk.count(b'\n')
        if nls != 0:
            open('/dev/pts/1', 'w').write(
                f'{nls}'
            )
        modified_chunk = chunk
        sys.stdout.buffer.write(modified_chunk)
        sys.stdout.flush()

if __name__ == '__main__':
    main()
