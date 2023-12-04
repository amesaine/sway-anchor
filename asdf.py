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
from enum import Enum
from functools import partial


class Orientation(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    NONE = "none"


class Order(Enum):
    PREV = 1
    NEXT = 2


class OriginalState():
    def __init__(self):
        self.container: Con = None
        self.fertile: Con = None
        self.anchor_parent_orientation: Orientation = None
        self.anchor_direction: Order = None
        self.anchor_fertile: Con = None


def find_fertile(c: Con) -> Dict[str, Con]:
    '''
    finds the ancestor that has more than 1 immediate child node,
    contrary to its name, this will also return workspace
    even if workspace only has 1 child node
    it also returns child node which contains the original
    focused container
    '''
    f_t = c
    fert = f_t.parent
    while len(fert.nodes) == 1 and fert.type != "workspace":
        f_t = fert
        fert = fert.parent
    return {"fertile": fert, "focused_tree_line": f_t}


def dive(c: Con, ori_sta: OriginalState) -> Con:
    '''Original_State
    by default, will get the first node in the layout, important
    when the current orientation is perpendicular to the orientation
    of the original container's parent.
    used for when the sibling comes after the original container.
    '''

    i = None
    if ori_sta.anchor_direction == Order.NEXT:
        i = 0
    elif ori_sta.anchor_direction == Order.PREV:
        i = -1

    # c is a window
    if c.orientation == Orientation.NONE.value:
        return c

    return dive(c.nodes[i], ori_sta)


def find_anchor(ori_sta: OriginalState) -> Con:
    result = find_fertile(ori_sta.container)
    # has immediate siblings
    fertile_nodes = result["fertile"].nodes
    ftl = result["focused_tree_line"]
    ftl_i = fertile_nodes.index(ftl)
    if ftl_i == 0:
        ori_sta.anchor_direction = Order.NEXT
        return dive(fertile_nodes[1], ori_sta)
    else:
        ori_sta.anchor_direction = Order.PREV
        return dive(fertile_nodes[ftl_i - 1], ori_sta)


def move(ori_sta: OriginalState) -> Dict[str, int]:
    # if immediate siblings
    fer = ori_sta.fertile
    foo = {"direction": None, "repeat": None}
    if fer == ori_sta.anchor_fertile:
        if ori_sta.anchor_direction == Order.PREV:
            foo["direction"] = "fuck all"
            foo["repeat"] = 0
        elif ori_sta.anchor_direction == Order.NEXT:
            if ori_sta.anchor_parent_orientation == Orientation.VERTICAL.value:
                foo["direction"] = "up"
                foo["repeat"] = 1
            elif ori_sta.anchor_parent_orientation == Orientation.HORIZONTAL.value:
                foo["direction"] = "left"
                foo["repeat"] = 1
    elif fer != ori_sta.anchor_fertile:
        if fer.orientation != ori_sta.anchor_parent_orientation:
            if fer.orientation == Orientation.HORIZONTAL.value:
                if ori_sta.anchor_direction == Order.PREV:
                    foo["direction"] = "right"
                    foo["repeat"] = 1
                elif ori_sta.anchor_direction == Order.NEXT:
                    foo["direction"] = "left"
                    foo["repeat"] = 1
            elif fer.orientation == Orientation.VERTICAL.value:
                if ori_sta.anchor_direction == Order.PREV:
                    foo["direction"] = "down"
                    foo["repeat"] = 1
                elif ori_sta.anchor_direction == Order.NEXT:
                    foo["direction"] = "up"
                    foo["repeat"] = 1
    return foo


def fullscreener(i3: Connection, e, ori_sta: OriginalState):
    fc: Con = i3.get_tree().find_focused()
    ori_sta.container = fc
    if "fullscreen-gaps" in fc.marks and fc.workspace().name != "fullscreen-gaps":
        anchor = find_anchor(ori_sta)
        ori_sta.fertile = find_fertile(ori_sta.container)["fertile"]
        ori_sta.anchor_parent_orientation = anchor.parent.orientation
        ori_sta.anchor_fertile = find_fertile(anchor)["fertile"]
        i3.command(f"[con_id={anchor.id}] focus, mark --add anchor;"
                   f"[con_id={fc.id}] focus;"
                   f"move container to workspace fullscreen-gaps,"
                   f"workspace fullscreen-gaps")
    elif "fullscreen-gaps" not in fc.marks and fc.workspace().name == "fullscreen-gaps":
        i3.command("move container to mark anchor, unmark anchor,"
                   "workspace back_and_forth")
        result = move(ori_sta)
        for i in range(result["repeat"]):
            i3.command(f'move {result["direction"]}')


def main():
    i3 = Connection()
    ori_sta = OriginalState()
    handler = partial(fullscreener, ori_sta=ori_sta)
    i3.on(Event.WINDOW_MARK, handler)
    i3.main()


if __name__ == "__main__":
    main()

