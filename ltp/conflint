#!/usr/bin/env python3

#
# Copyright (C) 2019  Wojtek Porczyk <woju@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

#
# usage: ./conflint < ltp.conf
#

import sys

def count_mistakes(file):
    mistakes = 0
    with file:
        prev = ''
        for i, line in enumerate(file):
            line = line.strip()
            if not line.startswith('['):
                continue
            if line < prev:
                print('bad order in line {i}: {line} (after {prev})'.format(
                    i=i, line=line, prev=prev))
                mistakes += 1
            prev = line
    return mistakes

def main(file=sys.stdin):
    return min(count_mistakes(file), 255)

if __name__ == '__main__':
    sys.exit(main())
