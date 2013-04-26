#!/usr/bin/env python2.7

from __future__ import print_function

import SocketServer
import argparse
import json
import lcm
import socket
import time
import threading
import sys
import Forseti

def main():
    print("starting videopile test...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data = {
        "ShowFlags":True,
        "ShowTimer":True,
        "Flags":
            [1,1,2,0,0,

             0,0,0,0,0,
             2,1,0,0,0,
             1,1,0,0,0],
        "LeftAllianceText":"Team A\nTeam B",
        "Time":"0:42",
        "MatchText":"Match <size=48>5</size>",
        "RightAllianceText":"Team C\nTeam D"
        }
    data_json = json.dumps(data)
    print("payload=" + data_json)

    while True:
        sock.sendto(data_json, ('10.20.34.104', 4999))
        time.sleep(1)


if __name__ == '__main__':
    main()
