rm -f /home/steam/themaid/tmuxout.log
mkfifo /tmp/tmuxpane
tmux pipe-pane -o -t csgo 'cat >> /tmp/tmuxpane'
tmux send-keys -t csgo $1 Space $2 Enter
sleep 1
cat /tmp/tmuxpane > /home/steam/themaid/tmuxout.log &
tmux pipe-pane -o -t csgo
rm -R /tmp/tmuxpane
