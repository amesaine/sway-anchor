#!/usr/bin/env python3

"""
idk

Copyright: jnzigg
e-mail: jnzig@proton.me
Project: https://github.com/jnzigg/sway-fullscreen-gaps
License: GPL3

Dependencies: python-i3ipc>=2.2.1 (i3ipc-python)
"""

from i3ipc import Connection, Con, Event
from typing import Dict, Tuple
from enum import Enum, auto
from functools import partial

# IDEA: start anchor, keep a stack of anchors originating from a
# base state, basically an undo tree for sway window management
# then be able to restart and use a new base state


class AnchorPosition(Enum):
    PREV = auto()
    NEXT = auto()


class Orientation(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    NONE = "none"

class ConWrapper:
    def __init__(self, con: Con = None):
        self.con = con
        self.anchor: Con = None
        self.anchor_position: AnchorPosition = None

    def __getattr__(self, name):
        return getattr(self.con, name)

    def find_fertile(self) -> Tuple[Con, Con]:
        origin = self.con
        fertile = origin.parent
        while len(fertile.nodes) == 1 and fertile.type != "workspace":
            origin = fertile
            fertile = fertile.parent
        return (fertile, origin)

    def anchor(self) -> Con:
        fertile, origin = self.find_fertile()

        def dive(c: Con, i: int) -> Con:
            # c is a window
            if c.orientation == Orientation.NONE.value:
                return c

            return dive(c.nodes[i], i)

        o_i = fertile.nodes.index(origin)
        anchor = None
        if o_i == 0:
            self.anchor_position = AnchorPosition.NEXT
            self.anchor = dive(fertile.nodes[1], 0)
        else:
            self.anchor_position = AnchorPosition.PREV
            self.anchor = dive(fertile.nodes[o_i - 1], 0)

        self._conn.command(f'[con_id={self.anchor.id}] mark --add anchor;'
                           f'[con_id={self.con.id}] mark --add anchored')
    
    def restore(self) -> Con:
        print(self.con.marks)


def anchorer(i3: Connection, e, conw: ConWrapper):
    root = i3.get_tree()
    fc = root.find_focused()
    if conw.con is None:
        conw.con = fc
    print(conw.marks, fc.marks)

def main():
    i3 = Connection()
    conw = ConWrapper()
    handler = partial(anchorer, conw=conw)
    i3.on(Event.WINDOW_MARK, handler)
    i3.main()


if __name__ == "__main__":
    main()

