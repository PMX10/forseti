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

class VideoPileBridge(object):

    def __init__(self, piemos_address, lc):
        self.lcm = lc
        self.out_address = piemos_address
        print('sending to address', self.out_address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lcm.subscribe('Video/Show', self.handle_show)
        self.lcm.subscribe('Video/VersusText', self.handle_versus_text)
        self.lcm.subscribe('Goals/Goals', self.handle_goals)
        self.lcm.subscribe('Timer/Time', self.handle_time)
        self.lcm.subscribe('ScoreKeeper/Score', self.handle_score)

    def start(self):
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._read_thread.start()

    def _read_loop(self):
        try:
            while True:
                self.lcm.handle()
        except:
            pass

    def send(self, msg):
        print("sending msg=" + msg)
        self.socket.sendto(msg, self.out_address)

    def handle_show(self, channel, data):
        print("Received Show packet")
        msg = Forseti.VideoShow.decode(data)
        self.send(json.dumps(
                {
                    "ShowFlags": bool(msg.ShowFlags),
                    "ShowTimer": bool(msg.ShowTimer),
                    "ShowScore": bool(msg.ShowScore),
                    "ShowSchedule": bool(msg.ShowSchedule),
                    "ShowShroud" : bool(msg.ShowShroud)
                    }
                ))

    def handle_versus_text(self, channel, data):
        print("Received Versus Text")
        msg = Forseti.VideoVersusText.decode(data)
        self.send(json.dumps(
                {
                    "LeftAllianceText": msg.LeftAllianceText,
                    "RightAllianceText": msg.RightAllianceText,
                    "MatchText": msg.MatchText
                    }
                ))
    def handle_goals(self, channel, data):
        print("Received Goals")
        msg = Forseti.GoalBoxes.decode(data)
        flags = []
        for goal in range (0,4):
            for box in range (0,5):
                flags.append(msg.goals[goal][box])
        self.send(json.dumps(
                {
                    "Flags": flags
                    }
                ))
    def handle_time(self, channel, data):
        print("Received Time")
        msg = Forseti.Time.decode(data)
        minutes = int(msg.game_time_so_far/ 60)
        seconds = msg.game_time_so_far % 60
        sec_str = str(seconds)
        if len(sec_str) == 1:
            sec_str = "0" + sec_str
        time = str(minutes) + ":" + sec_str

        self.send(json.dumps(
                {
                    "Time": time
                    }
                ))
    def handle_score(self, channel, data):
        print("Received Score")
        msg = Forseti.Score.decode(data)
        self.send(json.dumps(
                {
                    "LeftScore": msg.blue_finalscore,
                    "RightScore": msg.gold_finalscore,
                    }
                ))

def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-port', type=int, action='store')
    parser.add_argument('--remote-port', type=int, action='store')
    parser.add_argument('--remote-address', type=str, action='store')
    args = parser.parse_args()
    vals = [args.remote_address, args.remote_port, args.local_port]
    if any(vals) and not all(vals):
        print('Missing an argument')
        print('Should have remote-address, local-address, and local-port')
        print('Alternatively, only pass number')
        return
    bridge = VideoPileBridge((args.remote_address, args.remote_port), lc)
    bridge.start()
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
