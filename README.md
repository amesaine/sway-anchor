sway-anchor
===========

SwayWM script to undo container reparenting and restore original layout.

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

