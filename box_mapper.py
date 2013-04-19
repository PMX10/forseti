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
    args = parser.parse_args()
    teams = list(map(int, args.teams.split(',')))
    field_file = args.load or 'resources/field_mapping.json'
    field_objects = '[]'
    with open(field_file, 'r') as rfile:
        field_objects = rfile.read()
    print('Field map', field_objects)
    for i in range(len(teams)):
        send_team(lc, teams[i], i+1, field_objects)

def get_config(num):
    try:
        with open(os.path.join(config_dir, '{}.cfg'.format(num)), 
                  'r') as rfile:
            return rfile.read()
    except IOError:
        print('Could not get config for team {}'.format(num))
        try:
            with open(os.path.join(config_dir, 'default.cfg'), 'r') as rfile:
                return rfile.read()
        except IOError:
            print('Could not get default config.')

def get_name(num):
    return {}.get(num, 'Unknown team')

def send_team(lc, num, idx, field_objects):
    data = ConfigData()
    data.ConfigFile = get_config(num)
    data.IsBlueAlliance = idx < 2
    data.TeamNumber = int(num)
    data.TeamName = get_name(num)
    data.FieldObjects = field_objects
    lc.publish('PiEMOS' + str(idx) + '/Config', data.encode())

if __name__ == '__main__':
    main()
