cd ../rosbag
LAST_FILE=(ls -t|sed -n '1p')
rosbag paly $LAST_FILE
gnome-terminal --window -e 'bash -c "rqt_plot;exec bash"'

