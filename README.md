sway-anchor
===========

SwayWM script to undo container reparenting and restore original layout.

Demo
----

![Demo of the script in action](https://github.com/jnzigg/sway-anchor/blob/main/assets/demo.gif)

Base State:

|         |             |          |          |
|-------- | ----------- | -------- | -------- |
|         |             | Rickroll |          |
|Neovim   | wf-recorder | Ranger   | terminal |
|         |             | Nautilus |          |

1. Neovim, Rickroll, Ranger - Move to another workspace then undo state once.
2. Move Rickroll to the right.
3. Swap Nautilus with Ranger.
4. Undo state once.
5. Move ranger to another workspace.
6. Swap neovim with wf-recorder (terminal).
7. Undo state 3 times.

How it works
------------
1. Get state of currently focused window.
2. When moved or swapped:
     - Anchor focused window to another window which will serve as a reference for layout restoration.
     - Store the two windows' state.
3. On undo, move anchored window of the most recently tracked state to its anchor.
4. If necessary, move window up, down, left, or right, until original layout is restored.
5. Repeat

Installation
------------

Issues
------

TODO
----
- Error handling
- Refactoring
- Debug mode
- Tests (maybe)

