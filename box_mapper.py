#!/usr/bin/env python2.7
from __future__ import print_function

import argparse
import lcm
import os
import os.path

from Forseti import *

config_dir = 'configs'

def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, action='store')
    parser.add_argument('--teams', type=str, action='store')
    parser.add_argument('--config', const=True, action='store_const')
    parser.add_argument('--run', const=True, action='store_const')
    args = parser.parse_args()
    teams = []
    try:
        teams = list(map(int, args.teams.split(',')))
    except ValueError:
        print('Could not parse team list.')
        print('Please send a comma-separated list of numbers.')
    if args.config:
        do_config(lc, args, teams)
    if args.run:
        do_run(lc, args, teams)

def do_config(lc, args, teams):
    field_file = args.load or 'resources/field_mapping.json'
    field_objects = '[]'
    with open(field_file, 'r') as rfile:
        field_objects = rfile.read()
    #print('Field map', field_objects)
    for i in range(len(teams)):
        send_team(lc, teams[i], i, field_objects)

def do_run(lc, args, teams):
    print('Countdown.')

def get_config(num):
    try:
        with open(os.path.join(config_dir, '{}.cfg'.format(num)), 
                  'r') as rfile:
            config = rfile.read()
            #print('Team {} config:'.format(num), config)
            return config
    except IOError:
        print('Could not get config for team {}'.format(num))
        try:
            with open(os.path.join(config_dir, 'default.cfg'), 'r') as rfile:
                default_config = rfile.read()
                #print('Default config:', default_config)
                return default_config
        except IOError as e:
            print('Could not get default config.')
            raise e

def get_name(num):
    return {}.get(num, 'Unknown team')

def send_team(lc, num, idx, field_objects):
    data = ConfigData()
    data.ConfigFile = get_config(num)
    data.IsBlueAlliance = idx < 2
    data.TeamNumber = int(num)
    data.TeamName = get_name(num)
    data.FieldObjects = field_objects
    data.PiEMOSNumber = idx
    lc.publish('PiEMOS/Config', data.encode())

if __name__ == '__main__':
    main()
