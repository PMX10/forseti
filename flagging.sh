#!/bin/bash
urxvt -title "Flagger" -e sh -c  './Flagger.py'&
urxvt -title "goal_vis" -e sh -c  './goal_vis.py'&
urxvt -title "GoalReader" -e sh -c  './GoalReader.py'&
urxvt -title "MaestroDriver" -e sh -c  './MaestroDriver/MaestroDriver/bin/Debug/MaestroDriver.exe'
