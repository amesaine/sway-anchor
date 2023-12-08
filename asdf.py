#!/usr/bin/env python3

"""
idk

Copyright: jnzigg
e-mail: jnzig@proton.me
Project: https://github.com/jnzigg/sway-fullscreen-gaps
License: GPL3

Dependencies: python-i3ipc>=2.2.1 (i3ipc-python)
"""

# original state class
# current state class

from i3ipc import Connection, Con, Event
from typing import Dict
from enum import Enum, auto
from functools import partial


class Orientation(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    NONE = "none"


class Order(Enum):
    PREV = auto()
    NEXT = auto()


class Fertile:
    def __init__(self, container: Con, origin_line: Con):
        self.container = container
        self.origin_line = origin_line


class ConState:
    def __init__(self, container: Con = None):
        self._container: Con = None
        self._fertile: Fertile = None
        self._anchor: Con = None
        self.anchor_position: Order = None

        if container is not None:
            self._container = container

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container: Con):
        if self._container is not None:
            raise Exception(f"State is already set: {self._container.id}")

        if container is not None:
            self._container = container
            self._fertile = self.find_fertile()
            self._anchor = self.find_anchor()

    @property
    def fertile(self):
        return self._fertile

    @property
    def anchor(self):
        return self._anchor

    def find_fertile(self) -> Fertile:
        origin = self._container
        fertile = origin.parent
        while len(fertile.nodes) == 1 and fertile.type != "workspace":
            origin = fertile
            fertile = fertile.parent
        return Fertile(fertile, origin)

    def find_anchor(self) -> Con:
        f = self._fertile
        fn = f.container.nodes
        ol_i = fn.index(f.origin_line)

        def dive(c: Con, i: int) -> Con:
            # c is a window
            if c.orientation == Orientation.NONE.value:
                return c

            return dive(c.nodes[i], i)

        if ol_i == 0:
            self.anchor_position = Order.NEXT
            return dive(fn[1], 0)
        else:
            self.anchor_position = Order.PREV
            return dive(fn[ol_i - 1], -1)

    def return_con(self) -> Dict[str, int]:
        anchor = ConState(self.anchor)

        sequence: Dict[str, int] = None

        direction: Dict[tuple, str] = {
            (Order.NEXT, Orientation.HORIZONTAL.value,): "left",
            (Order.NEXT, Orientation.VERTICAL.value): "up",
            (Order.PREV, Orientation.HORIZONTAL.value): "right",
            (Order.PREV, Orientation.VERTICAL.value): "down",
        }

        # if immediate siblings
        if self.fertile == anchor.fertile:
            key = (self.anchor_position, anchor.container.parent.orientation)
            sequence["command"] = f"move {direction.get(key)}"

            if self.anchor_position == Order.NEXT:
                sequence["invoke"] = 1
            else:
                sequence["invoke"] = 0
        else:
            key = (self.anchor_position, self.fertile.container.orientation)
            sequence["command"] = f"move {direction.get(key)}"

            if self.fertile.container.orientation == anchor.container.parent.orientation:
                sequence["invoke"] = 2
            else:
                sequence["invoke"] = 1

        return sequence
    
    def reset(self):
        self._container = None
        self._anchor = None
        self._fertile = None
        self.anchor_position = None


def fullscreener(i3: Connection, e, focused: ConState):
    if focused.container is None:
        focused.container = i3.get_tree().find_focused()
    fc = focused.container

    if "fullscreen-gaps" in fc.marks and fc.workspace().name != "fullscreen-gaps":
        i3.command(f"[con_id={focused.anchor.id}] focus, mark --add anchor;"
                   f"[con_id={fc.id}] focus;"
                   f"move container to workspace fullscreen-gaps,"
                   f"workspace fullscreen-gaps")
    elif "fullscreen-gaps" not in fc.marks and fc.workspace().name == "fullscreen-gaps":
        i3.command("move container to mark anchor, unmark anchor,"
                   "workspace back_and_forth")
        sequence = focused.return_con()
        for i in range(sequence["invoke"]):
            i3.command(sequence["command"])
        focused.reset()


def main():
    i3 = Connection()
    focused = ConState()
    handler = partial(fullscreener, focused=focused)
    i3.on(Event.WINDOW_MARK, handler)
    i3.main()


if __name__ == "__main__":
    main()

