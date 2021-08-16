#!/bin/bash
# these are the tmux pane titles
# export CHAT_TITLE="chatwindowaeP8e"
# export ETON_TITLE="etoneeZ9wuxa"
export CHAT_TITLE="rex-chat-window"
export ETON_TITLE="rex-eton-cam"

# dimensions for our panes
ETON_WIDTH=45
CHAT_HEIGHT=12

# function to find a pane in tmux, returns the ID
find_pane () {
  TITLE=$1
  PANE_ID=$(tmux list-panes -as -f "#{==:#{pane_title},$TITLE}" -F '#D')
  echo $PANE_ID
}

new_pane() {
  TITLE=$1 ; shift 
  PANE_OPTS=$1 ; shift
  DIR=$1 ; shift
  CMDS=$*

  mypane=$(find_pane $TITLE)
  # echo "notes pane id \"$notespane\""
  if [ -n "${mypane}" ] ; then
   # pull that pane to our current window
   tmux join-pane ${PANE_OPTS} -s "${mypane}" > /dev/null
   # tmux join-pane -hbdl $NOTES_WIDTH -s "${notespane}" notespane=$(find_pane $NOTES_TITLE)
  else
   # or start a new pane
   mypane=$(tmux split-window ${PANE_OPTS} -P)
   tmux send-keys -t "${mypane}" "cd ${DIR}" C-m
   tmux send-keys -t "${mypane}" "printf '\033]2;%s\033\\' ${TITLE}" C-m
   tmux send-keys -t "${mypane}" 'sleep 1' C-m
   tmux send-keys -t "${mypane}" "$CMDS" C-m
  fi

  echo $mypane
}

first_pane=$(new_pane "$CHAT_TITLE" "-vfdl $CHAT_HEIGHT" "$HOME/github/rexroof/chat-window" "clear && source .env && ./chat-window")
second_pane=$(new_pane "$ETON_TITLE" \
  "-hdl $ETON_WIDTH -t $first_pane" \
  "$HOME/github/rexroof/stream/obs_follow_tmux" \
  "./tracker.py --pane ${ETON_TITLE} --source EtonBorder")
