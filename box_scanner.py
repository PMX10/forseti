#!/usr/bin/env python2.7
from __future__ import print_function

import json
import cmd
import atexit
import random

have_GoalReader = 'Maybe'
try:
    import GoalReader
    have_GoalReader = True
except ImportError:
    have_GoalReader = False
    print('Could not load GoalReader.')


MULTIPLY = 2
ADD = 1

def extract_reads(reads, objectId):
    out = []
    i = 0
    while i < len(reads):
        if reads[i].get(u'objectId', -1) == objectId:
            out.append(reads.pop(i))
        else:
            i += 1
    return out

class BoxScanCommander(cmd.Cmd):

    def __init__(self, *args, **kwargs):
        cmd.Cmd.__init__(self, *args, **kwargs)
        self.reads = []
        self.selected = []
        self.current_box = 0
        self.pcprox_reactor = GoalReader.PcProxReaderReactor(self.pcprox_read)
        self.grizzly_reactor = GoalReader.GrizzlyReaderReactor(self.grizzly_read)
        atexit.register(self.do_quit)
        self.normal_prompt = '  ready =>> '
        self.reading_prompt = 'reading =>> '
        self.mode = 'init'
        self.setup_normal_mode()

    @property
    def current_reads(self):
        if self.mode == 'select':
            return self.selected
        else:
            return self.reads

    def setup_normal_mode(self):
        self.mode = 'normal'
        self.prompt = self.normal_prompt

    def setup_reading_mode(self):
        self.mode = 'reading'
        self.prompt = 'reading =>> '

    def setup_select_mode(self):
        self.mode = 'select'
        self.prompt = 'select =>> '

    def emptyline(self):
        if self.mode == 'reading':
            self.goto_next_box()
        else:
            return cmd.Cmd.emptyline(self)

    def get_box(self, box_id):
        for read in self.reads:
            if read[u'objectId'] == box_id:
                return read

    def goto_next_box(self):
        while self.get_box(self.current_box):
            self.current_box += 1

    def do_done(self, rest=''):
        if self.mode != 'normal':
            self.setup_normal_mode()
        else:
            print('Already in normal mode.')

    def add_reads(self, read_list):
        if self.mode == 'select':
            for read in read_list:
                read = self.find_id(read[u'uid'])
                box = read[u'objectId']
                self.add_selected(box)
        else:
            for read in read_list:
                if not self.find_id(read[u'uid']):
                    print('New read:', read)
                    self.reads.append(read)

    def add_selected(self, box_id):
        for read in self.reads:
            if read[u'objectId'] ==  box_id and read not in self.selected:
                self.selected.append(read)

    def find_id(self, tag_id):
        for read in self.reads:
            if read[u'uid'] == tag_id:
                return read

    def do_read(self, rest=''):
        self.setup_reading_mode()

    def do_select(self, rest=''):
        self.setup_select_mode()

    def do_load(self, filename):
        try:
            with open(filename, 'r') as f:
                self.add_reads(json.load(f))
        except IOError as e:
            print('Could not open "{}".'.format(filename))
            print('Received error {}.'.format(e))

    def do_append(self, filename):
        try:
            with open(filename, 'r') as f:
                new_reads = json.load(f)
                i = 0
                while True:
                    current_reads = extract_reads(new_reads, i)
                    if not current_reads:
                        #print('Exiting, i =', i)
                        break
                    for read in current_reads:
                        read[u'objectId'] = self.current_box
                    #print(current_reads)
                    self.add_reads(current_reads)
                    self.current_box += 1
                    i += 1
        except IOError as e:
            print('Could not open "{}".'.format(filename))
            print('Received error {}.'.format(e))

    def convert_effects(self):
        for read in self.reads:
            if u'effect' in read:
                if read[u'effect'] == 'multiply':
                    read[u'objectType'] = MULTIPLY
                    del read[u'effect']
                elif read[u'effect'] == 'add':
                    read[u'objectType'] = ADD
                    del read[u'effect']

    def do_save(self, filename):
        self.convert_effects()
        try:
            with open(filename, 'w') as f:
                json.dump(self.current_reads, f, indent=True)
        except IOError as e:
            print('Could not open "{}".'.format(filename))
            print('Received error {}.'.format(e))

    def do_print(self, rest=''):
        print(json.dumps(self.current_reads, indent=True))

    def to_hex(self, tag_id):
        return hex(tag_id)[2:]

    def do_quit(self, rest=''):
        self.do_print('')
        print('Quitting.')
        return True

    def do_randomize(self, rest=''):
        effects = []
        for i in range(5):
            this_goal_effects = [MULTIPLY] + [ADD] * 4
            random.shuffle(this_goal_effects)
            effects.extend(this_goal_effects)
        effect_map = {}
        for read in self.current_reads:
            if read[u'objectId'] not in effect_map.keys():
                effect_map[read[u'objectId']] = effects.pop()
            read[u'objectType'] = effect_map[read[u'objectId']]

    def grizzly_read(self, reactor, idx, tag_id):
        print('.')
        self.add_reads([
            {
                u'readerType':u'Grizzly',
                u'uid':self.to_hex(tag_id),
                u'tagId':tag_id,
                u'objectType':1,
                u'objectId':self.current_box,
                }])

    def pcprox_read(self, reactor, idx, tag_id):
        print('.')
        self.add_reads([
            {
                u'readerType':u'pcProx',
                u'uid':self.to_hex(tag_id),
                u'tagId':tag_id,
                u'objectType':1,
                u'objectId':self.current_box,
                }])

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, action='store')
    parser.add_argument('--select', const=True, action='store_const')
    parser.add_argument('--randomize', const=True, action='store_const')
    parser.add_argument('--save', type=str, action='store')
    args = parser.parse_args()
    commander = BoxScanCommander()
    if args.load:
        commander.do_load(args.load)
    if args.select:
        commander.do_select()
    if args.randomize:
        commander.do_randomize()
    if args.save:
        commander.do_save(args.save)
    commander.cmdloop()

if __name__ == '__main__':
    main()
