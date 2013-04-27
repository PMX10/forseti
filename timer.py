#!/usr/bin/env python2.7
from __future__ import print_function

import Forseti
import configurator
import json
import lcm
import threading
import time
import os

class Node(object):

    def start_thread(self):
        self.thread = threading.Thread(target=self._loop)
        self.thread.daemon = True
        self.thread.start()

    def _loop(self):
        raise NotImplemented()

class Timer(object):

    def __init__(self):
        self.segments = []
        self.segment_start_time = time.time()
        self.running = False

    def _this_segment_time(self):
        return time.time() - self.segment_start_time

    def time(self):
        if self.running:
            return sum(self.segments) + self._this_segment_time()
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
        self.segments.append(self._this_segment_time())
        return self

    def add(self, additional_time):
        self.segments.append(additional_time)

    def subtract(self, less_time):
        self.segments.append(-less_time)

    def reset(self):
        self.__init__()
        return self

class Period(object):

    def __init__(self, name, length):
        self.name = name
        self.length = length

class MatchTimer(Node):

    def __init__(self, lc, match):
        self.lc = lc
        self.match = match
        self.stages = [Period("Setup", 5), Period("Autonomous", 20),
            Period("AutonomousPause", 0), Period("Teleop", 100),
            Period("End", 130)]
        self.stage_index = 0
        self.match_timer = Timer()
        self.stage_timer = Timer()
        self.lc.subscribe('Timer/Control', self.handle_control)
        self.start_thread()
        self.on_stage_change(None, self.stages[0])

    def reset(self):
        self.on_stage_change(self.stages[self.stage_index], self.stages[0])
        self.stage_index = 0
        self.match_timer.reset()
        self.stage_timer.reset()

    def current_stage(self):
        return self.stages[self.stage_index]

    def check_for_stage_change(self):
        if self.stage_timer.time() >= self.current_stage().length:
            self.on_stage_change(self.stages[self.stage_index - 1],
                self.stages[self.stage_index])
            self.stage_index += 1
            self.stage_timer.reset()
            self.stage_timer.start()

    def on_stage_change(self, old_stage, new_stage):
        if new_stage.name == 'Setup':
            self.match.stage = 'Autonomous'
            self.match.disable_all()
        elif new_stage.name == 'Autonomous':
            self.match.stage = 'Autonomous'
            self.match.enable_all()
        elif new_stage.name == 'AutonomousPause':
            self.match.stage = 'Paused'
            self.match.disable_all()
            self.pause()
        elif new_stage.name == 'Teleop':
            self.match.stage = 'Teleop'
            self.match.enable_all()

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
            self.match.time = int(self.match_timer.time())
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

class Team(object):

    def __init__(self, number):
        self.number = number
        self.name = configurator.get_name(number)
        self.teleop = False
        self.halt_radio = False
        self.auto = False
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled


class Match(object):

    def __init__(self, team_numbers):
        self.teams = [Team(num) for num in team_numbers]
        self.stage = 'Uknown'
        self.time = 0
        #self._teleop = False
        #self._autop = False

    #@property
    #def teleop(self):
        #return self._teleop

    #@teleop.setter
    #def teleop(self, val):
        #self._teleop = val

    #@property
    #def autop(self):
        #return self._autop

    #@autop.setter
    #def autop(self):
        #return self._autop

    def get_team(self, team_number):
        for team in self.teams:
            if team.number == team_number:
                return team

    def enable_all(self):
        for team in teams:
            team.enabled = True

    def disable_all(self):
        for team in teams:
            team.enabled = False



class ControlDataSender(Node):

    '''
{
	"ControlData":{
		"OperationMode":{
			"FieldTeleopEnabled":false, 
			"HaltRadio":false, 
			"FieldAutonomousEnabled":true, 
			"FieldRobotEnabled":true
		}, 
		"Match":{
			"Stage":"Setup", 
			"Time":44
		}
	}
}
    '''
    def __init__(self, lc, match):
        self.lc = lc
        self.match = match
        self.start_thread()

    def _loop(self):
        while True:
            for i in range(len(self.match.teams)):
                self.send(i + 1, self.match.teams[i])

    def send(self, piemos_num, team):
        msg = ControlData()
        msg.TeleopEnabled = self.match.stage == 'Teleop'
        msg.HaltRadio = False
        msg.AutonomousEnabled = self.match.stage == 'Autonomous'
        msg.RobotEnabled = team.enabled
        msg.Stage = self.match.stage
        msg.Time = self.match.time
        self.lc.publish('PiEMOS{}/Control'.format(piemos_num), msg.encode())


class RemoteTimer(object):

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


class Schedule(object):

    matches_filename_base = '{}.match'
    matches_dir = 'matches'

    def __init__(self):
        self.matches = []

    def clear(self):
        self.matches = []

    def load(self):
        self.clear()
        i = 1
        unread_matches = os.listdir(self.matches_dir)
        try:
            while True:
                filename = self.matches_filename_base.format(i)
                with open(os.path.join(self.matches_dir, filename)) as wfile:
                    self.matches.append(json.load(wfile))
                unread_matches.remove(filename)
                i += 1
        except IOError:
            # Couldn't find a match, assume we've loaded all the matches
            pass
        assert not unread_matches
        print(self.matches)
        

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
    sched = Schedule()
    sched.load()
    #print(configurator.get_team_name(2))
    #match = Match()
    #MatchTimer(lc).run()


if __name__ == '__main__':
    main()
