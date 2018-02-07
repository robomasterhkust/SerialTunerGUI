#!/bin/bash

gnome-terminal --window -e 'bash -c "roscore;exec bash"'
gnome-terminal --window -e 'bash -c "cd .. ;echo running serialTuner.py;python serialTuner.py; exec bash"' 


