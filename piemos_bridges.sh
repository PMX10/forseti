#!/bin/sh
for num in 1 2 3 4;
do
	command="urxvt -title \"PiEMOS$num\" -e sh -c  \"./piemos_bridge.py --number=$num\" &"
	echo $command
	sh -c "$command" &
done
