tmux attach -t termforge
tmux set -g set-clipboard off
tmux set -g focus-events off

rename pane title:
printf '\033]2;My Title\033\\'
