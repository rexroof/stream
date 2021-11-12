#!/bin/bash
PANE_TITLE=$1
PANE_ID=$(tmux list-panes -as -f "#{==:#{pane_title},$PANE_TITLE}" -F '#S:#I.#D')
tmux resize-pane -t ${PANE_ID} -Z 
