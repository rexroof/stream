#!/home/rex/.venv/xpybutil/bin/python
import xpybutil.ewmh as ewmh
import xpybutil.window as window
import subprocess
import sys
import simpleobsws, json, asyncio

# our x11 window title that we're looking for.
title = "Twitch Terminal"
# the tmux pane we're looking for.
pane_title = "findme"
# our obs source name that we're affecting
source_name = "orange"
# obs websocket details
obs_host = "127.0.0.1"
obs_port = 4444
obs_password = "rexroof"

# query xwindows for our window
xclients = ewmh.get_client_list().reply()
for c in xclients:
    if ewmh.get_wm_name(c).reply() == title:
        x11x, x11y, xwidth, xheight = window.get_geometry(c)

# quick sanity check if h/w are set
if not xwidth or xwidth < 1:
    sys.exit()
if not xheight or xheight < 1:
    sys.exit()

print(x11x, x11y, xwidth, xheight)

# x11x is the left/right location
# x11y is the up/down location

# subtract 38 pixels from top for menu


# query tmux for our pane
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
else:
    sys.exit()

print(tmux_window_height, tmux_window_width)
# check window active
# if array exists, if window_active_session == 0, and if window flags = -, or does not equal *

# subtract 60 from width and 120 from height for window decorations
# these mod values are roughly our character height/width
width_mod = (xwidth - 60) / tmux_window_width
height_mod = (xheight - 120) / tmux_window_height

# estimate pane height/width
pane_height_px = height_mod * tmux_pane_height
pane_width_px = width_mod * tmux_pane_width

# estimate the X/Y of where the pane is in the window
pane_offset_w_px = tmux_pane_left * width_mod
pane_offset_h_px = tmux_pane_top * height_mod

# this figures out the X/Y coordinates of our pane in the entire X11 view.
#  we are adding 30 & 60 pixels to compensate for window dressing.  (just guesses)
# placement_w =   window location + pane left * pixel mods
placement_w = x11x + 30 + pane_offset_w_px
# placement_h =   window location + pane top * pixel mods
placement_h = x11y + 60 + pane_offset_h_px

# geo="${pane_width_px%.*}x${pane_height_px%.*}+${placement_w%.*}+${placement_h%.*}"

# now for the OBS stuff
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host=obs_host, port=obs_port, password=obs_password, loop=loop)


async def move_cam():
    await ws.connect()

    data = {"item": source_name}
    result = await ws.call("GetSceneItemProperties", data)

    data = {
        "sourceName": source_name,
        "sourceSettings": {"height": 982, "width": 550},
        # "sourceSettings": {"height": pane_height_px, "width": pane_width_px},
    }
    print(data)
    result = await ws.call("SetSourceSettings", data)

    # geo="${pane_width_px%.*}x${pane_height_px%.*}+${placement_w%.*}+${placement_h%.*}"

    data = {
        "item": source_name,
        "visible": True,
        "position": {"y": 152, "x": 326},
        # "position": {"y": placement_h, "x": (placement_w - 2560)},
        # "scale.x": 1,
        # "scale.y": 1,
    }
    print(data)
    result = await ws.call("SetSceneItemProperties", data)

    await ws.disconnect()


loop.run_until_complete(move_cam())
