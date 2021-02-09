#!/bin/bash
set -x
SESSION="$USER-fpnet"
DATE=$(date +"%Y.%m.%d-%H:%M:%S")
LOGPATH="./logs/$DATE/"
if [ $# -lt 1 ]; then 
	echo "Usage: $0 <node number>"
	exit
fi
NODENUMBER=$1

sed -e "s/WORKER_COUNT = .*/WORKER_COUNT = $NODENUMBER/" -i code/config.py

sudo rm -rf "/tmp/chrome"
mkdir -p "/tmp/chrome"
sudo chown -R 1000:1000 "/tmp/chrome"
sudo chmod 777 "/tmp/chrome"
mkdir "$LOGPATH"

cd data/
rm fpnet_log.csv || true
ln -s "../$LOGPATH/fpnet_scan.csv" fpnet_log.csv
touch fpnet_log.csv
cd ../

cd core/
sudo docker-compose down 
cd ../

# Create session
tmux -2 new-session -d -s "$SESSION"


# Create panes
tmux split-window -v
tmux split-window -v
tmux select-pane -t 0
tmux split-window -h
tmux select-pane -t 0

# Send commands

tmux select-pane -t 1
tmux send-keys "htop" C-m
tmux select-pane -t 2
tmux send-keys "cd core/ && sudo docker-compose up fpnet_monitor | tee $LOGPATH/monitor" C-m
sleep 3
tmux select-pane -t 0
for i in $(seq 1 $NODENUMBER); do 
    tmux send-keys "cd core/ && sudo docker-compose up proxy$i 2>&1  > $LOGPATH/proxy$i &" C-m
    sleep 1
done
for i in $(seq 1 $NODENUMBER); do 
	tmux send-keys "cd core/ && sudo docker-compose up chrome$i 2>&1  > $LOGPATH/node$i &" C-m
    sleep 1
done
tmux send-keys "tail -f $LOGPATH/node* $LOGPATH/proxy*" C-m
sleep 10
tmux send-keys "cd core/ && tail -f $LOGPATH/node* | grep --line-buffered -v 'Timed out receiving message' " C-m
sleep 2
tmux select-pane -t 3
tmux send-keys "cd core/" C-m
tmux send-keys "# sudo docker-compose up fpnet_scanner | tee $LOGPATH/scanner" C-m 

tmux select-pane -t 3

# Attach to session
tmux -2 attach-session -t "$SESSION"
