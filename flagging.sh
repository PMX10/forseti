#!/bin/bash
urxvt -title "Flagger" -e sh -c  './Flagger.py'&
urxvt -title "GoalCounter" -e sh -c  './GoalCounter.py'&
urxvt -title "GoalReader" -e sh -c  './GoalReader.py'&
urxvt -title "MaestroDriver" -e sh -c  './MaestroDriver/MaestroDriver/bin/Debug/MaestroDriver.exe'
