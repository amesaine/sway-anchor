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
| Neovim  | wf-recorder | Ranger   | terminal |
|         |             | Nautilus |          |

1. Neovim, Rickroll, Ranger - Move to another workspace then undo state once.
2. Move Rickroll to the right.
3. Swap Nautilus with Ranger.
4. Undo state once.
5. Move ranger to another workspace.
6. Swap neovim with wf-recorder (terminal).
7. Undo state 3 times.

> [!NOTE]
> This script isn't polished and may or may not work on your setup. It may also fall in and out of my priorities.
> Regardless, feel free to open issues or pull requests.

Quickstart
------------

1. Copy/Download the [script][script] into `$HOME/bin`.
2. Start the daemon by adding this to sway config:

```
exec sway-anchor daemon start
```
> [!NOTE]
> This will only start the daemon on sway startup, not on config reload.

3. Set keybindings:

```
bindsym $mod+Control+u exec sway-anchor state undo
```

4. If you have keybinds to directionally swap containers ([example][swap-keybinds]), replace them with the script swap commands so the daemon can track their state. Currently, only directional swaps are supported.
```
bindsym $mod+Control+$left exec sway-anchor swap left
bindsym $mod+Control+$down exec sway-anchor swap down
bindsym $mod+Control+$up exec sway-anchor swap up
bindsym $mod+Control+$right exec sway-anchor swap right
```
5. See `sway-anchor -h` and `sway-anchor [command] -h` for more info.

How it works
------------
1. Get state of currently focused window.
2. When moved or swapped:
     - Anchor focused window to another window which will serve as a reference for layout restoration.
     - Store the two windows' state.
3. On undo, move anchored window of the most recently tracked state to its anchor.
4. If necessary, move window up, down, left, or right, until original layout is restored.
5. Repeat

Motivation
-----------
I wanted to "fullscreen" a window while still having window gaps and a status bar. This essentially is just moving it to another workspace as a solo container. The problem was that when moving it back to it's original workspace, the layout wasn't restored. This was not easily fixable with builtin sway commands.

Through sway-anchor, it's now doable with this simple bash script (**sway-fullscreen-gaps**):
```sh
#!/bin/sh

active_ws=$(swaymsg -t get_workspaces -r \
    | jq -r '.[] | select(.focused==true).name')

if [ "$active_ws" != "fullscreen-gaps" ]; then
    swaymsg move container to workspace fullscreen-gaps
    swaymsg workspace fullscreen-gaps
else
    sway-anchor state undo
fi
```

Then add this to your sway config:
```
bindsym $mod+f exec sway-fullscreen-gaps
```


FAQ
---
### 1. Sometimes, the layout restoration doesn't work properly.
Besides error handling not being implemented yet, this script isn't supposed to handle all edge cases. Specific edge case
support will only be supported if enough people need it. Using [sway-autotiling][sway-autotiling] with `--limit 2`, this
script works perfectly.

### 2. Will state redo functionality be implemented?
No plans as of yet. Although it's a fairly simple feature to add, I personally think having too much ways to navigate a system can be prone
to decision paralysis. If enough people voice their need for it, it will be supported.

TODO
----
- Error handling
- Refactoring
- Debug mode
- Tests (maybe)


[script]: https://github.com/jnzigg/sway-anchor/blob/main/sway-anchor
[swap-keybinds]: https://www.reddit.com/r/swaywm/comments/mmhvyf/swap_mode/
[sway-autotiling]: https://github.com/nwg-piotr/autotiling
