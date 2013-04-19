#!/usr/bin/env python2.7
import lcm
import time

#from exlcm import example_t
from Forseti import Flags
from Forseti import CommandData

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = CommandData()
msg.command = "Reset"

#msg = Flags()
#msg.goals = [[2, 2, 2, 2, 2], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]

lc.publish("PiEMOS1/Command", msg.encode())
lc.publish("PiEMOS2/Command", msg.encode())
lc.publish("PiEMOS3/Command", msg.encode())
lc.publish("PiEMOS4/Command", msg.encode())
