#!/home/rex/.venv/xpybutil/bin/python
import subprocess
import sys

title = "Twitch Terminal"
pane_title = "findme"

# xwininfo -frame -name "${WINTITLE}" | grep -E 'Width:|Height:|Corners:' > $XWIN_TMP
xwin_output = subprocess.check_output(["xwininfo", "-name", title], text=True)

xwininfo = {}
for line in xwin_output.split("\n"):
    if ":" in line:
        parts = line.split(":", 1)
        xwininfo[parts[0].strip()] = parts[1].strip()

xwin_width = int(xwininfo["Width"])
xwin_height = int(xwininfo["Height"])
xwin_corners = xwininfo["Corners"].split()[0]
xwin_corners_width = xwin_corners.split("+")[1]
xwin_corners_height = xwin_corners.split("+")[2]

tmux_format = "#T #{window_width} #{window_height} #{pane_bottom} #{pane_top} #{pane_height} #{pane_right} #{pane_left} #{pane_width} #{window_active_sessions} #{window_flags}"
tmux_output = subprocess.check_output(
    [
        "tmux",
        "list-panes",
        "-af",
        "#{==:#{pane_title}," + pane_title + "}",
        "-F",
        tmux_format,
    ],
    text=True,
)

tmux_specs = tmux_output.split()

if len(tmux_specs) > 0:
    tmux_window_width = int(tmux_specs[1])
    tmux_window_height = int(tmux_specs[2])
    tmux_pane_bottom = int(tmux_specs[3])
    tmux_pane_top = int(tmux_specs[4])
    tmux_pane_height = int(tmux_specs[5])
    tmux_pane_right = int(tmux_specs[6])
    tmux_pane_left = int(tmux_specs[7])
    tmux_pane_width = int(tmux_specs[8])
    tmux_window_active_sessions = tmux_specs[9]
    tmux_window_flags = tmux_specs[10]

# check window active
# if array exists, if window_active_session == 0, and if window flags = -, or does not equal *

# subtract 60 from width and 120 from height for window decorations
width_mod = (xwin_width - 60) / tmux_window_width
height_mod = (xwin_height - 120) / tmux_window_height
