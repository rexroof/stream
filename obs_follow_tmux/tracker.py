#!/home/rex/.venv/xpybutil/bin/python
from time import sleep
import simpleobsws
import asyncio
import logging
import os
import argparse


parser = argparse.ArgumentParser(description="OBS Camera Tracker")

parser.add_argument(
    "--pane",
    dest="pane_title",
    default="cam-pane",
    help="pane title to use, and target",
)

parser.add_argument(
    "--source", dest="source_name", default="camera-source", help="OBS Source to target"
)

parser.add_argument(
    "--visibility",
    help="change visibility when window changes",
    dest="toggle_visible",
    action="store_true",
)
parser.add_argument(
    "--no-visibility",
    help="do not change visibility when window changes",
    dest="toggle_visible",
    action="store_false",
)
parser.set_defaults(toggle_visible=True)

args = parser.parse_args()

# our x11 window title that we're looking for.
title = "Twitch Terminal"
# the tmux pane we're looking for.
# pane_title = "findme"
# pane_title = "cam-ohSh4Eak"
pane_title = args.pane_title
# our obs source name that we're affecting
# source_name = "orange"
# source_name = "floatycam"
source_name = args.source_name

# obs websocket details
obs_host = "127.0.0.1"
obs_port = 4444
obs_password = "rexroof"

# this is the scaling of our desktop inside obs.
# default_scaling = 0.9
default_scaling = 0.75

# whether to do cropping
docropping = False

# depending on if we're streaming our left or right desktop,
#  set this to the width of the main desktop
# w_offset = 2560
w_offset = 0

# are we toggling visibility?
change_visible = args.toggle_visible


def set_visible(setting=None):
    if change_visible:
        return setting
    else:
        return True


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

    tmux_format = "#T #{window_width} #{window_height} #{pane_top} #{pane_left} #{pane_height} #{pane_width} #{pane_active} #{window_active} #{window_active_sessions} #{window_flags}"
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

    if len(tmux_specs) > 0 and len(tmux_specs) < 11:
        print(tmux_specs)
        return None
    elif len(tmux_specs) == 11:
        logging.debug(tmux_specs)
        result["tmux_window_width"] = int(tmux_specs[1])
        result["tmux_window_height"] = int(tmux_specs[2])
        result["tmux_pane_top"] = int(tmux_specs[3])
        result["tmux_pane_left"] = int(tmux_specs[4])
        result["tmux_pane_height"] = int(tmux_specs[5])
        result["tmux_pane_width"] = int(tmux_specs[6])
        result["tmux_pane_active"] = int(tmux_specs[7])
        result["tmux_window_active"] = int(tmux_specs[8])
        result["tmux_window_active_sessions"] = int(tmux_specs[9])
        result["tmux_window_flags"] = tmux_specs[10]
    else:
        return None

    if not result["tmux_window_flags"]:
        return None

    logging.debug(
        f"tmux_window_active_sessions {result['tmux_window_active_sessions']}"
    )

    if result["tmux_window_active_sessions"] == 0:
        return None

    logging.debug(f"tmux_window_active {result['tmux_window_active']}")

    if result["tmux_window_active"] == 0:
        return None

    logging.debug(f"tmux_pane_active {result['tmux_pane_active']}")
    if "Z" in result["tmux_window_flags"] and (result["tmux_pane_active"] == 0):
        return None

    logging.debug(f"tmux_window_flags {result['tmux_window_flags']}")
    if "*" not in result["tmux_window_flags"]:
        return None

    return result


async def main_loop(previous={}):
    visible = set_visible(True)
    xinfo = await window_info(title)
    side_cropping = 0
    top_cropping = 0

    # x11x is the left/right location
    # x11y is the up/down location

    if xinfo is None:
        visible = set_visible(False)

    # we should check  xdotool getactivewindow getwindowname
    # to see if we are the active window, if not, pass

    active = await active_window()
    logging.debug(f"{active} {title}")
    if active != title:
        visible = set_visible(False)
    if active is None:
        visible = set_visible(False)

    if visible:
        # remove 26 characters for the tmux status bar
        # xinfo["xheight"] -= 26

        tmuxinfo = await tmux_info(pane_title)

        if tmuxinfo is None:
            visible = set_visible(False)

    if visible:
        # these mod values are roughly our character height/width
        width_mod = xinfo["xwidth"] / tmuxinfo["tmux_window_width"]
        # +1 here is to add back the tmux status bar
        height_mod = xinfo["xheight"] / (tmuxinfo["tmux_window_height"] + 1)

        # estimate pane height/width
        pane_height_px = height_mod * tmuxinfo["tmux_pane_height"]
        pane_width_px = width_mod * tmuxinfo["tmux_pane_width"]

        # pane_left is the actual separator column (aka |)
        # pane top is also the separator row (aka ---- )
        # estimate the X/Y of where the pane is in the window
        pane_offset_w_px = (tmuxinfo["tmux_pane_left"]) * width_mod
        pane_offset_h_px = (tmuxinfo["tmux_pane_top"]) * height_mod

        # this figures out the X/Y coordinates of our pane in the entire X11 view.
        # placement_w =   window location + pane left * pixel mods
        placement_w = xinfo["x11x"] + pane_offset_w_px
        # placement_h =   window location + pane top * pixel mods
        placement_h = xinfo["x11y"] + pane_offset_h_px

    data = {"item": source_name}
    result = await ws.call("GetSceneItemProperties", data)

    # if our scene item doesn't exist in current scene, eject!
    if result["status"] == "error":
        return previous

    # double checking our current scene has our camera in it
    if "visible" not in result:
        visible = set_visible(False)

    if visible:
        new_y = placement_h * default_scaling
        new_x = (placement_w - w_offset) * default_scaling
        new_scaling_y = (pane_height_px * default_scaling) / result["sourceHeight"]
        new_scaling_x = (pane_width_px * default_scaling) / result["sourceWidth"]

        if docropping:
            source_aspect = result["sourceWidth"] / result["sourceHeight"]
            pane_aspect = pane_width_px / pane_height_px
        else:
            source_aspect = 1
            pane_aspect = 1

        print(f"scaling_x: {new_scaling_x} scaling_y: {new_scaling_y}")

        if pane_aspect < source_aspect:
            # pin height, crop sides
            new_scaling_x = new_scaling_y
            s_width = result["sourceWidth"] * new_scaling_x
            side_cropping = abs(s_width - pane_width_px) / 2
            side_cropping = side_cropping * result["sourceWidth"] / s_width
            # side_cropping = side_cropping * new_scaling_x

            print(f"pane_height {pane_height_px} swidth {s_width}")
            print(f"top crop: {top_cropping}")
            print(f"side crop: {side_cropping}")

        elif pane_aspect > source_aspect:
            # pin width, crop top/bottom
            new_scaling_y = new_scaling_x
            s_height = result["sourceHeight"] * new_scaling_y
            top_cropping = abs(s_height - pane_height_px) / 2
            top_cropping = top_cropping * result["sourceHeight"] / s_height
            # side_cropping = side_cropping * new_scaling_x
            # top_cropping = top_cropping * new_scaling_y

            print(f"pane_width {pane_width_px} sheight {s_height}")
            print(f"top crop: {top_cropping}")
            print(f"side crop: {side_cropping}")

    else:
        new_x = result["position"]["x"]
        new_y = result["position"]["y"]
        new_scaling_x = result["scale"]["x"]
        new_scaling_y = result["scale"]["y"]

    if not visible:
        data = {"item": source_name, "visible": visible}
    else:
        data = {
            "item": source_name,
            "visible": visible,
            "crop": {
                "bottom": top_cropping,
                "left": side_cropping,
                "right": side_cropping,
                "top": top_cropping,
            },
            "position": {"y": new_y, "x": new_x},
            "scale": {"y": new_scaling_y, "x": new_scaling_x},
        }
    logging.debug(data)
    if data == previous:
        logging.debug("skipping write, data the same")
    else:
        result = await ws.call("SetSceneItemProperties", data)
    # returning data to track as previous
    return data


logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


async def forever():

    # dict for keeping track of the previous data we sent to obs
    previous = {
        "item": source_name,
        "crop": {"bottom": 0, "left": 0, "right": 0, "top": 0},
        "visible": False,
        "position": {"y": 0, "x": 0},
        "scale": {"y": 1.0, "x": 1.0},
    }
    # your infinite loop here, for example:
    await ws.connect()
    while True:
        previous = await main_loop(previous)
        sleep(0.50)
    await ws.disconnect()


# now for the OBS stuff
loop = asyncio.get_event_loop()

ws = simpleobsws.obsws(host=obs_host, port=obs_port, password=obs_password, loop=loop)
loop.run_until_complete(forever())
