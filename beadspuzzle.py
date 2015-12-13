#!/usr/bin/env python3
# vim: set et ts=4 sw=4:
# Written for python 3.5

"""
Solution to my daughter's beads packing puzzle, [Goo-Seul] puzzle in Korean.

It seems that finding all possible solutions needs
very long time (NP-complete). Thus let user place some pieces
before this program solve() with the rest of pieces.
Of course, user can invoke solve() right away, without any placement.
---
Copyright (c) 2015, Jaesup Kwak veshboo@gmail.com
This software is released under the BSD License. See the LICENSE file for
more information.
"""

import signal
import sys
import curses
import atexit
import time

"""
* board

@
@@
@@@
@@@@
@@@@@
@@@@@@
@@@@@@@
@@@@@@@@
@@@@@@@@@
@@@@@@@@@@

Elements correspond holes not occupied by a piece.
That is, not-yet-solved parts. In other words, board is
a 'set' of holes and we keep only empty holes in progress
of finding solutions.
"""
_board = {(x, y) for y in range(10) for x in range(10-y)}

"""
* piece

(x,y)           - for a bead in a piece
[(x,y)...]      - a piece oriented
[[(x,y)...]...] - possible orientations of a piece
"""

"""
@    @@   @@    @
@@   @     @   @@
"""
_piece_3 = ('a',
            [[(0, 0), (1, 0), (0, 1)],
             [(0, 0), (0, 1), (1, 1)],
             [(0, 1), (1, 1), (1, 0)],
             [(0, 0), (1, 0), (1, 1)]])

"""
@@@@  @
      @
      @
      @
"""
_piece_4_a = ('b',
              [[(0, 0), (1, 0), (2, 0), (3, 0)],
               [(0, 0), (0, 1), (0, 2), (0, 3)]])

"""
@@
@@
"""
_piece_4_b = ('c',
              [[(0, 0), (1, 0), (0, 1), (1, 1)]])

"""
@    @@  @@@   @
@@@  @     @   @
     @        @@

  @  @   @@@  @@
@@@  @   @     @
     @@        @
"""
_piece_4_c = ('d',
              [[(0, 0), (1, 0), (2, 0), (0, 1)],
               [(0, 0), (0, 1), (0, 2), (1, 2)],
               [(0, 1), (1, 1), (2, 1), (2, 0)],
               [(0, 0), (1, 0), (1, 1), (1, 2)],
               [(0, 0), (1, 0), (2, 0), (2, 1)],
               [(0, 0), (1, 0), (0, 1), (0, 2)],
               [(0, 0), (0, 1), (1, 1), (2, 1)],
               [(0, 2), (1, 2), (1, 1), (1, 0)]])

"""
 @
@@@
 @
"""
_piece_5_a = ('e',
              [[(1, 0), (1, 1), (1, 2), (0, 1), (2, 1)]])

"""
@      @@  @@@@    @
@@@@   @      @    @
       @           @
       @          @@

   @   @   @@@@   @@
@@@@   @   @       @
       @           @
       @@          @
"""
_piece_5_b = ('f',
              [[(0, 0), (1, 0), (2, 0), (3, 0), (0, 1)],
               [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)],
               [(0, 1), (1, 1), (2, 1), (3, 1), (3, 0)],
               [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)],
               [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
               [(0, 0), (1, 0), (0, 1), (0, 2), (0, 3)],
               [(0, 0), (0, 1), (1, 1), (2, 1), (3, 1)],
               [(1, 0), (1, 1), (1, 2), (1, 3), (0, 3)]])

"""
 @     @   @@@@    @
@@@@   @@    @     @
       @          @@
       @           @

  @    @   @@@@    @
@@@@   @    @     @@
       @@          @
       @           @
"""
_piece_5_c = ('g',
              [[(0, 0), (1, 0), (2, 0), (3, 0), (1, 1)],
               [(0, 0), (0, 1), (0, 2), (0, 3), (1, 2)],
               [(0, 1), (1, 1), (2, 1), (3, 1), (2, 0)],
               [(1, 0), (1, 1), (1, 2), (1, 3), (0, 1)],
               [(0, 0), (1, 0), (2, 0), (3, 0), (2, 1)],
               [(0, 0), (0, 1), (0, 2), (0, 3), (1, 1)],
               [(0, 1), (1, 1), (2, 1), (3, 1), (1, 0)],
               [(1, 0), (1, 1), (1, 2), (1, 3), (0, 2)]])

"""
  @@   @     @@@  @
@@@    @    @@    @@
       @@          @
        @          @

@@      @   @@@    @
 @@@   @@     @@   @
       @          @@
       @          @
"""
_piece_5_d = ('h',
              [[(0, 0), (1, 0), (2, 0), (2, 1), (3, 1)],
               [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1)],
               [(0, 0), (1, 0), (1, 1), (2, 1), (3, 1)],
               [(0, 2), (0, 3), (1, 0), (1, 1), (1, 2)],
               [(0, 1), (1, 1), (1, 0), (2, 0), (3, 0)],
               [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)],
               [(0, 1), (1, 1), (2, 1), (2, 0), (3, 0)],
               [(0, 0), (0, 1), (1, 1), (1, 2), (1, 3)]])

"""
  @   @      @@   @@
 @@   @@    @@     @@
@@     @@   @       @
"""
_piece_5_e = ('i',
              [[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
               [(0, 1), (0, 2), (1, 1), (1, 0), (2, 0)],
               [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)],
               [(0, 2), (1, 2), (1, 1), (2, 1), (2, 0)]])

"""
@    @@@  @@@    @
@    @      @    @
@@@  @      @  @@@
"""
_piece_5_f = ('j',
              [[(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],
               [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
               [(0, 2), (1, 2), (2, 2), (2, 1), (2, 0)],
               [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)]])

"""
@ @  @@   @@@   @@
@@@  @    @ @    @
     @@         @@
"""
_piece_5_g = ('k',
              [[(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)],
               [(0, 0), (1, 0), (0, 1), (0, 2), (1, 2)],
               [(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)],
               [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]])

"""
@@   @@  @@@    @
@@@  @@   @@   @@
     @         @@

 @@  @   @@@   @@
@@@  @@  @@    @@
     @@         @
"""
_piece_5_h = ('l',
              [[(0, 0), (1, 0), (1, 1), (0, 1), (2, 0)],
               [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1)],
               [(1, 0), (2, 0), (2, 1), (1, 1), (0, 1)],
               [(0, 0), (1, 0), (1, 1), (0, 1), (1, 2)],
               [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1)],
               [(0, 0), (1, 0), (1, 1), (0, 1), (0, 2)],
               [(0, 0), (1, 0), (1, 1), (0, 1), (2, 1)],
               [(1, 0), (1, 1), (1, 2), (0, 2), (0, 1)]])

_pieces = [
    _piece_3,
    _piece_4_a,
    _piece_4_b,
    _piece_4_c,
    _piece_5_a,
    _piece_5_b,
    _piece_5_c,
    _piece_5_d,
    _piece_5_e,
    _piece_5_f,
    _piece_5_g,
    _piece_5_h,
]


def print_piece(piece_oriented):
    display = [[0]*5 for t in range(5)]
    for bead in piece_oriented:
        display[bead[1]][bead[0]] = 1
    # For terminal print out, we go high valued y first
    for row in reversed(display):
        # Skip empty rows to save lines for terminal display
        # there are no empty rows after a non-empty row
        empty_row = 1
        for cell in row:
            if cell == 1:
                empty_row = 0
                break
        if empty_row == 1:
            continue
        # Non-empty row
        for cell in row:
            if cell == 1:
                print("o", end="")
            else:
                print(" ", end="")
        print()
    print()


# DEBUG _pieces[0 .. 11]
# for piece in _pieces:
#     print('piece_id = ', piece[0])
#     for o in piece[1]:
#         print_piece(o)
# exit(0)


"""
move piece to x, y
with a specified bead as handle
"""


def mov0(o, bead, x, y):
    dx = x - bead[0]
    dy = y - bead[1]
    to = list()
    for (bx, by) in o:
        to.append((bx + dx, by + dy))
    return to


"""
Move piece to x, y with the first bead as handle
"""


def mov(o, x, y):
    return mov0(o, o[0], x, y)


"""
Move piece to x, y with origin (0, 0) as handle
"""


def mov_by_origin(o, x, y):
    return mov0(o, (0, 0), x, y)


"""
check if fit or not
o - Orientation of a piece
"""


def fit(board, to):
    for tb in to:
        if tb not in board:
            return False
    return True


"""
put/unput a piece oriented at a position

unput is not used because we create new board
for next level solve().  Instead of modify a board
with put() and restore with unput().
"""


def put(board, to):
    for tb in to:
        board.remove(tb)


def unput(board, to):
    for tb in to:
        board.add(tb)


"""
Fail/reject check for remaining pieces
not to traverse or iterate impossible solution tree.
making sure that there is no empty holes that does
not fit for any piece.

TODO Data structure like 'Dancing Links' helps Algorithm X ???
"""


def fail(board, pieces):
    # test if puttable with board
    # but add beads to tmp_board
    # short path check with tmp_board
    tmp_board = set()
    for (x, y) in board:
        h_good = False
        if (x, y) in tmp_board:
            continue
        for piece in pieces:
            for o in piece[1]:
                for bead in o:
                    to = mov0(o, bead, x, y)
                    if fit(board, to):
                        for bead in to:
                            tmp_board.add(bead)
                        h_good = True
                        break
                if h_good:
                    break
            if h_good:
                break
        if not h_good:
            return True
    return False


def print_solution(sol):
    display = [[0]*(10-t) for t in range(10)]
    for (c, to) in sol:
        for (bx, by) in to:
            display[by][bx] = c
    for row in reversed(display):
        for cell in row:
            if cell == 0:
                print('-', end='')
            else:
                print(cell, end='')
        print()


"""
Solution: (references)
- Backtracking algorithm
- Knuth's algorithm X
- Sudoku, Pentomino
"""


def solve(board, pieces, px, sol, found):
    if fail(board, pieces[px:]):
        return found
    if len(board) == 0:
        print('Found={}:'.format(found + 1))
        # Time elapsed
        # global t1, t2
        # t2 = time.clock()
        # print('Elapsed={}:'.format(t2 - t1))
        # t1 = t2
        print_solution(sol)
        return found + 1
    for o in pieces[px][1]:
        for (x, y) in board:
            to = mov(o, x, y)
            if fit(board, to):
                sol.append((pieces[px][0], to))
                # Duplicate solutions was found
                # due to put/unput modifies order of holes
                # in board that we iterate on
                new_board = set()
                for h in board:
                    new_board.add(h)
                put(new_board, to)
                found = solve(new_board, pieces, px + 1, sol, found)
                sol.pop()
    return found


"""
Below we place some pieces using curses UI.
The placed pieces are removed from the pieces, with which
the solve() works, because they are already placed by user.
Placed pieces are modeled as list of [p, o, x, y]
enough to 'put()' them before start solve().

TODO actually, _placed is temporary, we can do by directly
calling put(). this require 'p' for piece, does not change
depending on put() order.
"""
_placed = list()


"""
Palette keep orientations of each pieces
"""
_palette = [0 for t in range(12)]


def c_draw_piece(w, wx, wy, p, o):
    for (bx, by) in _pieces[p][1][o]:
        w.addch(wy - by, wx + bx, _pieces[p][0])


def c_draw_palette(w, palette):
    p = 0
    for x in range(12):
        c_draw_piece(w, x*6 + 1, 15 + 1, p, palette[p])
        p += 1


def c_draw_selector(w, p):
    for t in range(6):
        w.addch(12, p*6 + t, '*')
        w.addch(12 + 5, p*6 + t, '*')
        w.addch(12 + t, p*6, '*')
        w.addch(12 + t, p*6 + 5, '*')


def c_draw_placed(w, placed, p):
    for y in range(10):
        for x in range(10 - y):
            w.addch(9 - y, x, '-')
    # Draw selected piece last
    # or some beads can be hidden by other pieces
    for (p2, o, x, y) in placed:
        if p2 != p:
            c_draw_piece(w, 0 + x, 9 - y, p2, o)
    for (p2, o, x, y) in placed:
        if p2 == p:
            w.attron(curses.A_REVERSE)
            c_draw_piece(w, 0 + x, 9 - y, p2, o)
            w.attroff(curses.A_REVERSE)


def c_display(w, palette, p, placed, message):
    w.clear()
    c_draw_palette(w, palette)
    c_draw_selector(w, p)
    c_draw_placed(w, placed, p)
    w.addstr(18, 0, message)
    w.refresh()


def signal_handler(signal, frame):
    print()
    print("! Interrupt by Control-C")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    _w = curses.initscr()
    atexit.register(curses.endwin)
    curses.curs_set(0)
    curses.noecho()
    curses.nonl()
    _w.keypad(1)

    _p = 0
    _key = 0
    _quit = 0
    _run = 0
    _message = ''
    while _quit == 0:
        c_display(_w, _palette, _p, _placed, _message)
        _w.addstr(15, 72, "<==")
        _w.addstr(19, 0, "(Select mode)")
        _w.addstr(20, 0, "Arrows    : Browse to select")
        _w.addstr(21, 0, "Space     : Rotate the selected piece")
        _w.addstr(22, 0, "Enter     : to Place mode")
        _w.addstr(23, 0, "r         : run/solve the puzzle            q : quit")
        _w.refresh()
        _key = _w.getch()
        _message = ''
        if _key == ord('q'):
            _quit = 1
        elif _key == ord('r'):
            _quit = 1
            _run = 1
        elif _key == curses.KEY_RIGHT:
            _p += 1
            if _p == 12:
                _p = 0
        elif _key == curses.KEY_LEFT:
            _p -= 1
            if _p == -1:
                _p = 11
        elif _key == ord(' '):
            # Rotate on palette
            _palette[_p] += 1
            if _palette[_p] == len(_pieces[_p][1]):
                _palette[_p] = 0
            # Rotate on board placed
            for t in _placed:
                # t [p, o, x, y]
                if t[0] == _p:
                    old_o = t[1]
                    t[1] = _palette[_p]
                    to = mov_by_origin(_pieces[_p][1][t[1]], t[2], t[3])
                    if not fit(_board, to):
                        _message = "! Piece placed out of board"
                        t[1] = _palette[_p] = old_o
                    break;
        elif _key in (curses.KEY_ENTER, ord('\r'), ord('\n')):
            f = list()
            for t in _placed:
                if t[0] == _p:
                    f = t
                    break
            else:
                # f [p, o, x, y]
                f = [_p, _palette[_p], 0, 0]
                _placed.append(f)
            while _quit == 0:
                c_display(_w, _palette, _p, _placed, _message)
                _w.addstr(6, 15, "<==")
                _w.addstr(19, 0, "(Place mode)")
                _w.addstr(20, 0, "Arrows    : Move the selected piece on the board")
                _w.addstr(21, 0, "Space     : Rotate the selected piece")
                _w.addstr(22, 0, "Enter     : Put and to Select mode")
                _w.addstr(23, 0, "d         : Delete and to Select mode       q : quit")
                _w.refresh()
                _key = _w.getch()
                _message = ''
                old_o, old_x, old_y = f[1], f[2], f[3]
                if _key == ord('q'):
                    _quit = 1
                elif _key in (curses.KEY_ENTER, ord('\r'), ord('\n')):
                    break
                elif _key == ord('d'):
                    _placed.remove(f)
                    break
                elif _key == curses.KEY_UP:
                    if f[3] < 9:
                        f[3] += 1
                elif _key == curses.KEY_DOWN:
                    if f[3] > 0:
                        f[3] -= 1
                elif _key == curses.KEY_RIGHT:
                    if f[2] < 9:
                        f[2] += 1
                elif _key == curses.KEY_LEFT:
                    if f[2] > 0:
                        f[2] -= 1
                elif _key == ord(' '):
                    f[1] += 1
                    if f[1] == len(_pieces[_p][1]):
                        f[1] = 0
                    _palette[_p] = f[1]
                else:
                    _message = "! Invalid key pressed"
                # Check out of bound, then cancel movement
                if old_o != f[1] or old_x != f[2] or old_y != f[3]:
                    to = mov_by_origin(_pieces[_p][1][f[1]], f[2], f[3])
                    if not fit(_board, to):
                        _message = "! Piece placed out of board"
                        f[1] = _palette[_p] = old_o
                        f[2], f[3] = old_x, old_y
        else:
            _message = "! Invalid key pressed"

    curses.endwin()
    atexit.unregister(curses.endwin)

    if _run:
        _sol = []
        _found = 0
        # put placed to board
        for (p, o, x, y) in _placed:
            to = mov_by_origin(_pieces[p][1][o], x, y)
            if fit(_board, to):
                put(_board, to)
                _sol.append((_pieces[p][0], to))
            else:
                print("! Cannot put a piece as specified... Overwrapped?")
                exit(1)
        # pieces remain to solve with := _pieces - placed
        _pieces_remain = list()
        for p in range(len(_pieces)):
            is_placed = False
            for placed in _placed:
                if placed[0] == p:
                    is_placed = True
                    break
            if not is_placed:
                _pieces_remain.append(_pieces[p])
        # t1 = t2 = time.clock()
        solve(_board, _pieces_remain, 0, _sol, _found)

