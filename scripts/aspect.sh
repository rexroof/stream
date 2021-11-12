#!/bin/bash

PANE_TITLE=$1
DIRECTION=${2:-down}
PANE_ID=$(tmux list-panes -as -f "#{==:#{pane_title},$PANE_TITLE}" -F '#S:#I.#D')
PANE_WIDTH=$(tmux list-panes -af "#{==:#{pane_title},${PANE_TITLE}}" -F "#{pane_width}")
PANE_HEIGHT=$(tmux list-panes -af "#{==:#{pane_title},${PANE_TITLE}}" -F "#{pane_height}")

# calculate these
# NEW_HEIGHT=14
# NEW_WIDTH=47

if [ "${DIRECTION}" = "down" ] ; then 
  NEW_HEIGHT=$( bc <<< "${PANE_WIDTH} * 0.27" | cut -f1 -d\. )
  NEW_WIDTH=${PANE_WIDTH}
else
  NEW_HEIGHT=${PANE_HEIGHT}
  NEW_WIDTH=$( bc <<< "${PANE_HEIGHT} * 3.6"  | cut -f1 -d\. )
fi

tmux resize-pane -t "${PANE_ID}" -y $NEW_HEIGHT -x $NEW_WIDTH

# 47 x 13  # rex
# 54 x 15  # eton
