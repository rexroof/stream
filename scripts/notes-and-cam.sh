#!/bin/bash
# these are the tmux pane titles
# export CAM_TITLE="cam-ohSh4Eak"
# export NOTES_TITLE="notes-quie0aeX"
export CAM_TITLE="rex-cam"
export NOTES_TITLE="rex-notes"

# dimensions for our panes
NOTES_WIDTH=40
CAM_HEIGHT=10

# function to find a pane in tmux, returns the ID
find_pane () {
  TITLE=$1
  PANE_ID=$(tmux list-panes -as -f "#{==:#{pane_title},$TITLE}" -F '#S:#I.#D')
  echo $PANE_ID
}

# NOTES FIRST
notespane=$(find_pane $NOTES_TITLE)
# echo "notes pane id \"$notespane\""
if [ -n "${notespane}" ] ; then
 # pull that pane to our current window
 tmux join-pane -hbdl $NOTES_WIDTH -s "${notespane}"
 notespane=$(find_pane $NOTES_TITLE)
else
 # or start a new pane
 notespane=$(tmux split-window -hbdl $NOTES_WIDTH -P)
 tmux send-keys -t ${notespane} 'cd /home/rex/github/rexroof/stream/' C-m
 tmux send-keys -t ${notespane} "printf '\033]2;%s\033\\' ${NOTES_TITLE}" C-m
 tmux send-keys -t ${notespane} 'sleep 1' C-m
 tmux send-keys -t ${notespane} 'vi notes' C-m
fi

# NOW CAM
campane=$(find_pane $CAM_TITLE)
if [ -n "${campane}" ] ; then
 # pull that pane to our current window
 tmux join-pane -t ${notespane} -vbdl $CAM_HEIGHT -s "${campane}"
else
 # or start a new pane
 campane=$(tmux split-window -t ${notespane} -vbdl $CAM_HEIGHT -P)
 tmux send-keys -t ${campane} 'cd /home/rex/github/rexroof/stream/obs_follow_tmux/' C-m
 tmux send-keys -t ${campane} "printf '\033]2;%s\033\\' ${CAM_TITLE}" C-m
 tmux send-keys -t ${campane} "clear ; figlet CAM ; ./tracker.py --pane ${CAM_TITLE} --source floatycam" C-m
fi
