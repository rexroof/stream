#!/home/rex/.venv/xpybutil/bin/python
import subprocess
import sys
import pprint
import simpleobsws, json, asyncio
import logging
import os


# our x11 window title that we're looking for.
title = "Twitch Terminal"
# the tmux pane we're looking for.
pane_title = "findme"
# our obs source name that we're affecting
# source_name = "orange"
source_name = "floatycam"
# obs websocket details
obs_host = "127.0.0.1"
obs_port = 4444
obs_password = "rexroof"


async def window_info(title="window title"):
    result = {}

    proc = await asyncio.create_subprocess_shell(
        f"xwininfo -name '{title}'",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if stdout:
        xwin_output = stdout.decode()
    else:
        if stderr:
            logging.warning(stderr.decode())
        return None
    # t=[line for line in s.splitlines() if ":" in line]
    # res={line.split(": ")[0]: line.split(": ")[1] for line in t}
    for line in xwin_output.split("\n"):
        if "Absolute upper-left X" in line:
            result["x11x"] = int(line.split(":")[1].strip())
        elif "Absolute upper-left Y" in line:
            result["x11y"] = int(line.split(":")[1].strip())
        elif "Width" in line:
            result["xwidth"] = int(line.split(":")[1].strip())
        elif "Height" in line:
            result["xheight"] = int(line.split(":")[1].strip())
    # quick sanity check if h/w are set
    if not result["xwidth"] or result["xwidth"] < 1:
        return None
    if not result["xheight"] or result["xheight"] < 1:
        return None
    logging.debug(f"window_info {result}")

    return result


async def active_window():
    proc = await asyncio.create_subprocess_shell(
        "xdotool getactivewindow getwindowname",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return stdout.decode().splitlines()[0]
    else:
        if stderr:
            logging.warning(stderr.decode())
        return None


# query tmux for our pane
async def tmux_info(pane_title="findme"):
    result = {}

    tmux_format = "#T #{window_width} #{window_height} #{pane_top} #{pane_left} #{pane_height} #{pane_width} #{window_active_sessions} #{window_flags}"
    cmd = (
        "tmux list-panes -af '#{==:#{pane_title},"
        + pane_title
        + "}' -F '"
        + tmux_format
        + "'"
    )
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        tmux_specs = stdout.decode().split()
    else:
        if stderr:
            logging.warning(stderr.decode())
        return None

    if len(tmux_specs) > 0:
        logging.debug(tmux_specs)
        result["tmux_window_width"] = int(tmux_specs[1])
        result["tmux_window_height"] = int(tmux_specs[2])
        result["tmux_pane_top"] = int(tmux_specs[3])
        result["tmux_pane_left"] = int(tmux_specs[4])
        result["tmux_pane_height"] = int(tmux_specs[5])
        result["tmux_pane_width"] = int(tmux_specs[6])
        result["tmux_window_active_sessions"] = int(tmux_specs[7])
        result["tmux_window_flags"] = tmux_specs[8]
    else:
        return None

    logging.debug("tmux geometry: {result}")

    if not result["tmux_window_flags"]:
        return None

    print(f"tmux_window_active_sessions {result['tmux_window_active_sessions']}")
    if result["tmux_window_active_sessions"] == 0:
        return None

    print(f"tmux_window_flags {result['tmux_window_flags']}")
    if result["tmux_window_flags"] != "*":
        return None

    return result


async def main_loop():
    visible = True

    xinfo = await window_info(title)

    # x11x is the left/right location
    # x11y is the up/down location

    if xinfo is None:
        visible = False

    # we should check  xdotool getactivewindow getwindowname
    # to see if we are the active window, if not, pass

    active = await active_window()
    logging.debug(f"{active} {title}")
    if active != title:
        visible = False
    if active is None:
        visible = False

    if visible:
        # remove 26 characters for the tmux status bar
        xinfo["xheight"] -= 26

        tmuxinfo = await tmux_info(pane_title)

        if tmuxinfo is None:
            visible = False

    if visible:
        # these mod values are roughly our character height/width
        width_mod = xinfo["xwidth"] / tmuxinfo["tmux_window_width"]
        height_mod = xinfo["xheight"] / tmuxinfo["tmux_window_height"]

        # estimate pane height/width
        pane_height_px = height_mod * tmuxinfo["tmux_pane_height"]
        pane_width_px = width_mod * tmuxinfo["tmux_pane_width"]

        # estimate the X/Y of where the pane is in the window
        pane_offset_w_px = tmuxinfo["tmux_pane_left"] * width_mod
        pane_offset_h_px = tmuxinfo["tmux_pane_top"] * height_mod

        # this figures out the X/Y coordinates of our pane in the entire X11 view.
        # placement_w =   window location + pane left * pixel mods
        placement_w = xinfo["x11x"] + pane_offset_w_px
        # placement_h =   window location + pane top * pixel mods
        placement_h = xinfo["x11y"] + pane_offset_h_px

    await ws.connect()

    data = {"item": source_name}
    result = await ws.call("GetSceneItemProperties", data)

    # everything is *0.9 because my desktop is scaled to 0.9 in OBS

    if not visible:
        data = {"item": source_name, "visible": visible}
    else:
        data = {
            "item": source_name,
            "visible": visible,
            "position": {"y": (placement_h * 0.9), "x": ((placement_w - 2560) * 0.9)},
            "scale": {
                "y": ((pane_height_px * 0.9) / result["sourceHeight"]),
                "x": ((pane_width_px * 0.9) / result["sourceWidth"]),
            },
        }
    print(data)
    result = await ws.call("SetSceneItemProperties", data)

    await ws.disconnect()


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


# now for the OBS stuff
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host=obs_host, port=obs_port, password=obs_password, loop=loop)
loop.run_until_complete(main_loop())
