#!/usr/bin/env python3

"""
idk

Copyright: jnzigg
e-mail: jnzig@proton.me
Project: https://github.com/jnzigg/sway-fullscreen-gaps
License: GPL3

Dependencies: python-i3ipc>=2.2.1 (i3ipc-python)
"""


from i3ipc import Connection, Con, Event, events
from typing import List, Dict
from enum import Enum


class Orientation(Enum):
    VERTICAL = 1
    HORIZONTAL = 2


class Order(Enum):
    PREV = 1
    NEXT = 2


def find_fertile(c: Con) -> Dict[str, Con]:
    '''
    finds the ancestor that has more than 1 immediate child node,
    contrary to its name, this will also return workspace
    even if workspace only has 1 child node
    it also returns child node which contains the original
    focused container
    '''
    f_t = c
    fert = c.parent
    while len(fert.nodes) == 1 and fert.type != "workspace":
        f_t = fert
        fert = fert.parent
    return {"fertile": fert, "focused_tree_line": f_t}


def dive(c: Con, ord: Order) -> Con:
    '''
    by default, will get the first node in the layout, important
    when the current orientation is perpendicular to the orientation
    of the original container's parent.
    used for when the sibling comes after the original container.
    '''

    i = None
    if ord == Order.NEXT:
        i = 0
    elif ord == Order.PREV:
        i = -1

    # c is a window
    if c.orientation == "none":
        return c

    return dive(c.nodes[i], ord)


def find_anchor(original_con: Con) -> Con:
    result = find_fertile(original_con)
    # has immediate siblings
    fertile_nodes = result["fertile"].nodes
    ftl = result["focused_tree_line"]
    ftl_i = fertile_nodes.index(ftl)
    if ftl_i == 0:
        return dive(fertile_nodes[1], Order.NEXT)
    else:
        return dive(fertile_nodes[ftl_i - 1], Order.PREV)


def handler(i3: Connection, e):
    fc: Con = i3.get_tree().find_focused()
    if "fullscreen-gaps" in fc.marks and fc.workspace().name != "fullscreen-gaps":
        anchor = find_anchor(fc)
        i3.command(f"[con_id={anchor.id}] focus, mark --add anchor;"
                   f"[con_id={fc.id}] focus;"
                   f"move container to workspace fullscreen-gaps,"
                   f"workspace fullscreen-gaps")
    elif "fullscreen-gaps" not in fc.marks and fc.workspace().name == "fullscreen-gaps":
        i3.command("move container to mark anchor, unmark anchor,"
                   "workspace back_and_forth")


def main():
    i3 = Connection()
    original_orientation: Orientation = None
    i3.on(Event.WINDOW_MARK, handler)
    i3.main()


if __name__ == "__main__":
    main()
