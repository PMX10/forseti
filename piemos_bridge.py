#!/usr/bin/env python2.7
from __future__ import print_function

import SocketServer
import argparse
import json
import lcm
import socket
import time
from Forseti import *

class PiEMOSBridge(object):

    def __init__(self, piemos_address, number, lc):
        self.lcm = lc
        self.out_address = piemos_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.lcm.subscribe('PiEMOS/Config', self.handle_config)
        #self.lcm.subscribe('PiEMOS/Command', self.handle_command)
        self.lcm.subscribe('PiEMOS/Control', self.handle_control)
        self.number = number

    def send(self, msg):
        self.socket.sendto(msg, self.out_address)

    def handle_config(self, channel, data):
        assert channel == 'PiEMOS/Config'
        msg = ConfigData.decode(data)
        if msg.PiEMOSNumber != self.number:
            return
        self.send(json.dumps({
            'ConfigFile': msg.ConfigFile,
            'IsBlueAlliance': msg.IsBlueAlliance,
            'TeamNumber': msg.TeamNumber,
            'TeamName': msg.TeamName,
            'FieldObjects': msg.FieldObjects
        }))
        assert channel == 'PiEMOS/Command'
        msg = CommandData.decode(data)
        self.send(json.dumps({
            'Command': msg.command
        }))

    def handle_control(self, channel, data):
        assert channel == 'PiEMOS/Control'
        msg = ControlData.decode(data)
        self.send(json.dumps({
            'ControlData': {
                'OperationMode': {
                    'FieldTeleopEnabled': msg.TeleopEnabled,
                    'HaltRadio': msg.HaltRadio,
                    'FieldAutonomousEnabled': msg.AutonomousEnabled, 
                    'FieldRobotEnabled': msg.RobotEnabled
                }, 
                'Match':{
                    'Stage':msg.Stage, 
                    'Time': msg.time
                }
            }
        }))

class PiEMOSHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        print('Got packet from PiEMOS')
        msg = self.request[0]
        if 'Health' in msg:
            self.handle_health(msg)
        elif 'ConfigDataFeedback' in msg:
            self.handle_config_feedback(msg)

    def handle_health(self, packet):
        print('Got PiEMOS health', packet)
        msg = json.loads(packet)
        msg = msg['Health']
        health = PiEMOSHealth()
        health.TeleopEnabled = msg['OperationMode']['FieldTeleopEnabled']
        health.LocalRobotEnabled = msg['OperationMode']['LocalRobotEnabled']
        health.AutonomousEnabled = msg['OperationMode']['FieldAutonomousEnabled']
        health.FieldRobotEnabled = msg['OperationMode']['FieldRobotEnabled']
        health.Stage = msg['Match']['Stage']
        health.Time = msg['Match']['Time']
        health.Uptime = msg['Uptime']
        health.PiEMOSState = msg['PiEMOSState']
        self.publish('PiEMOS/Health', health)

    def handle_config_feedback(self, msg):
        print('Get PiEMOS config feedback', msg)
        feedback = ConfigFeedback()
        feedback.ConfigDataMd5 = msg['ConfigDataFeedback']['ConfigDataMd5']
        self.publish('PiEMOS/ConfigFeedback', msg)

    def publish(self, topic, msg):
        self.server.publish(topic, msg)

class PiEMOSReceiver(SocketServer.UDPServer):

    def __init__(self, lc, in_addr):
        SocketServer.UDPServer.__init__(self, in_addr, PiEMOSHandler)
        self.lcm = lc

    def publish(self, topic, msg):
        self.lcm.publish(topic, msg.encode())


def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, action='store')
    parser.add_argument('--port', type=int, action='store')
    parser.add_argument('--number', type=int, action='store')
    args = parser.parse_args()
    if not args.address:
        print('Need address!')
        return
    bridge = PiEMOSBridge(args.address, args.number, lc)
    piemos_receiver = PiEMOSReceiver(lc, ('', args.port)).serve_forever()


if __name__ == '__main__':
    main()
