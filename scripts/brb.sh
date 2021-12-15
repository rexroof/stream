#!/bin/bash

# aquarium
# watch flowers
# nyancat
# cmatrix
# watch fortune

# ytop
# bottom
# glances
# htop


msg="$*"
if [ -z "$msg" ] ; then
  msg="BRB"
fi
funbox="docker run --rm -it wernight/funbox"

item[0]="sleep 1 ; $funbox cmatrix"
item[1]="$HOME/.venv/glances/bin/glances"
item[2]="watch -n 10 -t flowers you deserve this"
item[3]="sleep 1 ; $funbox nyancat"
# item[4]="env DISPLAY='' mpv --no-audio --really-quiet --quiet --loop=yes -vo=caca 'https://www.youtube.com/watch?v=FJ4RcqOpipo'"
item[4]="env DISPLAY='' mpv --no-audio --really-quiet --quiet --loop=yes -vo=caca 'https://www.youtube.com/watch?v=T8PKButEb0w'"
item[5]="$funbox asciiquarium"
item[6]="$HOME/bin/ytop"
item[7]="$HOME/bin/btm"
item[8]="htop"
item[9]="neofetch"
item[10]="cpufetch"
item[11]="archey"
item[12]="sleep 1 ; watch -t -n 30 $funbox fortune"
item[13]="pipes-rs"
# todo #  item[10]="sleep 1; bashtop"
#  https://github.com/aristocratos/bashtop
# rand=$[$RANDOM % ${#item[@]}]
# echo $(date)
# echo ${item[$rand]}

rand=$[$RANDOM % ${#item[@]}]
tmux new-window "${item[$rand]}"
unset item[$rand]
item=( "${item[@]}" )


rand=$[$RANDOM % ${#item[@]}]
tmux split-window -h "${item[$rand]}"
unset item[$rand]
item=( "${item[@]}" )

rand=$[$RANDOM % ${#item[@]}]
tmux split-window -h "${item[$rand]}"
unset item[$rand]
item=( "${item[@]}" )

rand=$[$RANDOM % ${#item[@]}]
tmux split-window -h "${item[$rand]}"
unset item[$rand]
item=( "${item[@]}" )

rand=$[$RANDOM % ${#item[@]}]
tmux split-window -h "${item[$rand]}"
unset item[$rand]
item=( "${item[@]}" )

$HOME/bin/chat-window.sh
tmux select-layout tiled >> /dev/null

# top 
# tmux split-window -bvfl 10 sh -c "sleep 1 ; toilet --metal --font 'mono9' -t --directory \"$HOME/github/figlet-fonts\" \"$msg\" ; sh"
# tmux split-window -bvfl 10 sh -c "sleep 1 ; toilet --metal --font 'future' -t --directory \"$HOME/github/figlet-fonts\" \"$msg\" ; sh"
tmux split-window -bvfl 8 sh -c "sleep 1 ; toilet --metal --font 'ANSI Shadow' -t --directory \"$HOME/github/figlet-fonts\" \"$msg\" ; sh"
