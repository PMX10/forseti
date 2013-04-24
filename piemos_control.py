#!/usr/bin/env python2.7
from __future__ import print_function

import argparse
import lcm
import os
import os.path
import time
import threading
import math

from Forseti import *

def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, action='store')
    parser.add_argument('--teams', type=str, action='store')
    args = parser.parse_args()

    msg = ControlData()
    msg.TeleopEnabled = False
    msg.HaltRadio = False
    msg.AutonomousEnabled = False
    msg.RobotEnabled = False
    msg.Stage = "Setup"
    msg.Time = 0

    start = time.time()
    '''
    while True:
        msg.TeleopEnabled = True
        msg.AutonomousEnabled = False
        msg.RobotEnabled = True
        msg.Stage = "Teleop"
        msg.Time = round(time.time() - start)
        lc.publish("PiEMOS4/Control", msg.encode())
        print("sending control, time=" + str(msg.Time))
        time.sleep(0.25)
    '''

    while time.time() - start < 2:
        msg.Time = round(time.time() - start)
        print("sending setup, time=" + str(msg.Time))
        msg.AutonomousEnabled = True
        msg.TeleopEnabled = False
        msg.RobotEnabled = False
        msg.Stage = "Setup"
        lc.publish("PiEMOS1/Control", msg.encode())
        lc.publish("PiEMOS2/Control", msg.encode())
        lc.publish("PiEMOS3/Control", msg.encode())
        lc.publish("PiEMOS4/Control", msg.encode())
        time.sleep(0.25)

    '''
    while time.time() - start < 17:
        msg.Time = round(time.time() - start)
        msg.AutonomousEnabled = True
        msg.TeleopEnabled = False
        msg.RobotEnabled = True
        msg.Stage = "Autonomous"
        print("sending control, time=" + str(msg.Time))
        lc.publish("PiEMOS4/Control", msg.encode())
        time.sleep(0.25)
    '''
    while True:
        msg.Time = round(time.time() - start)
        msg.AutonomousEnabled = False
        msg.TeleopEnabled = True
        msg.RobotEnabled = True
        msg.Stage = "Teleop"
        print("sending teleop, time=" + str(msg.Time))
        lc.publish("PiEMOS1/Control", msg.encode())
        lc.publish("PiEMOS2/Control", msg.encode())
        lc.publish("PiEMOS3/Control", msg.encode())
        lc.publish("PiEMOS4/Control", msg.encode())
        ztime.sleep(0.25)




if __name__ == '__main__':
    main()
