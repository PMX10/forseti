#!/usr/bin/env python2.7
from __future__ import print_function

import lcm
import time
import Forseti
import threading

class Timer(object):

    def __init__(self):
        self.segments = []
        self.segment_start_time = time.time()
        self.running = False

    def this_segment_time(self):
        return time.time() - self.segment_start_time

    def time(self):
        if self.running:
            return sum(self.segments) + self.this_segment_time()
        else:
            return sum(self.segments)

    def start(self):
        self.running = True
        self.segment_start_time = time.time()
        return self

    def pause(self):
        if not self.running:
            print('Timer already paused!')
            return self
        self.running = False
        self.segments.append(self.this_segment_time())
        return self

    def add(self, additional_time):
        self.segments.append(additional_time)

    def subtract(self, less_time):
        self.segments.append(-less_time)

    def reset(self):
        self.__init__()

class Period(object):

    def __init__(self, name, length):
        self.name = name
        self.length = length

class MatchTimer(object):

    def __init__(self, lc):
        self.lc = lc
        self.stages = [Period("Setup", 5), Period("Autonomous", 20),
            Period("AutonomousPause", 5), Period("Teleop", 100),
            Period("End", 130)]
        self.stage_index = 0
        self.match_timer = Timer()
        self.stage_timer = Timer()
        self.lc.subscribe('Timer/Control', self.handle_control)
        self.start_thread()

    def start_thread(self):
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    def current_stage(self):
        return self.stages[self.stage_index]

    def check_for_stage_change(self):
        if self.stage_timer.time() >= self.current_stage().length:
            self.stage_index += 1
            self.stage_timer.reset()
            self.stage_timer.start()

    def start(self):
        self.match_timer.start()
        self.stage_timer.start()

    def _loop(self):
        while True:
            self.lc.handle()

    def pause(self):
        self.stage_timer.pause()
        self.match_timer.pause()

    def reset_stage(self):
        self.stage_timer.reset()
        self.match_timer.stop()

    def reset_match(self):
        self.stage_index = 0
        self.stage_timer.reset()
        self.match_timer.reset()

    def start(self):
        self.stage_timer.start()
        self.match_timer.start()

    def run(self):
        while self.stage_index < len(self.stages):
            time.sleep(0.5)
            self.check_for_stage_change()
            msg = Forseti.Time()
            msg.game_time_so_far = self.match_timer.time()
            msg.stage_time_so_far = self.stage_timer.time()
            msg.total_stage_time = self.current_stage().length
            msg.stage_name = self.current_stage().name
            #print('Sending', msg)
            print('.')
            self.lc.publish('Timer/Time', msg.encode())

    def handle_control(self, channel, data):
        msg = Forseti.TimeControl.decode(data)
        print('Received command', msg.command_name)
        {
            'pause': self.pause,
            'start': self.start,
            'reset_match': self.reset_match,
            'reset_stage': self.reset_stage
        }[msg.command_name]()


class Remote(object):

    def __init__(self):
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')

    def send(self, command):
        print('Sending', command)
        msg = Forseti.TimeControl()
        msg.command_name = command
        self.lc.publish('Timer/Control', msg.encode())

    def pause(self):
        self.send('pause')

    def start(self):
        self.send('start')

    def reset_match(self):
        self.send('reset_match')

    def reset_stage(self):
        self.send('reset_stage')


def test():
    t = Timer()
    time.sleep(1)
    print('Should be 0', t.time())
    t.start()
    time.sleep(1)
    print('Should be 1', t.time())
    time.sleep(1)
    print('Should be 2', t.time())
    t.pause()
    time.sleep(1)
    print('Should be 2', t.time())
    t.start()
    time.sleep(1)
    print('Should be 3', t.time())
    time.sleep(1)
    print('Should be 4', t.time())


def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    MatchTimer(lc).run()


if __name__ == '__main__':
    main()
