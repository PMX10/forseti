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
from Forseti import *

class PiEMOSBridge(object):

    def __init__(self, piemos_address, number, lc):
        self.lcm = lc
        self.out_address = piemos_address
        print('sending to address', self.out_address)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        assert number in range(1, 5)
        self.lcm.subscribe('PiEMOS' + str(number) + '/Config', self.handle_config)
        self.lcm.subscribe('PiEMOS' + str(number) + '/Command', self.handle_command)
        self.lcm.subscribe('PiEMOS' + str(number) + '/Control', self.handle_control)
        print("Subscribed to=" + 'PiEMOS' + str(number) + '/Config')
        self.number = number
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True

    def start(self):
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

    def handle_config(self, channel, data):
        assert channel == 'PiEMOS' + str(self.number) + '/Config'
        print("Received config packet")
        msg = ConfigData.decode(data)
        fieldobjects = json.loads(msg.FieldObjects)
        self.send(json.dumps({
            'ConfigData': {
                'TeamName': msg.TeamName,
                'FieldObjects': fieldobjects,
                #'FieldObjects': [],
                'ConfigFile': msg.ConfigFile.replace('\t','').replace('\n', '').replace('\r', ''),
                #'ConfigFile':'',
                'TeamNumber': msg.TeamNumber,
                'IsBlueAlliance': bool(msg.IsBlueAlliance)
            }
        }))

    def handle_command(self, channel, data):
        assert channel == 'PiEMOS' + str(self.number) + '/Command'
        msg = CommandData.decode(data)

        print("Sending Command=" + str(msg.command))
        self.send(json.dumps({
            'Command': msg.command
        }))

    def handle_control(self, channel, data):
        print("Got control packet")
        assert channel == 'PiEMOS' + str(self.number) + '/Control'
        print("control packet has correct channel...")
        msg = ControlData.decode(data)
        print("Sending control=" + str(msg.HaltRadio))
        self.send(json.dumps({
            'ControlData': {
                'OperationMode': {
                    'FieldTeleopEnabled': bool(msg.TeleopEnabled),
                    'HaltRadio': bool(msg.HaltRadio),
                    'FieldAutonomousEnabled': bool(msg.AutonomousEnabled), 
                    'FieldRobotEnabled': bool(msg.RobotEnabled)
                }, 
                'Match':{
                    'Stage':msg.Stage, 
                    'Time': msg.Time
                }
            }
        }))

class PiEMOSHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        print('Got packet from PiEMOS')
        msg = self.request[0]
        #print(msg)
        if 'Health' in msg:
            self.handle_health(msg)
        elif 'ConfigDataFeedback' in msg:
            self.handle_config_feedback(msg)

    def handle_health(self, packet):
        #print('Got PiEMOS health', packet)
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
        self.publish('PiEMOS' + str(self.server.number) + '/Health', health)

    def handle_config_feedback(self, msg):
        print('Get PiEMOS config feedback', msg)
        data = json.loads(msg)
        feedback = ConfigFeedback()
        feedback.ConfigDataMd5 = data['ConfigDataFeedback']['ConfigDataMd5']
        self.publish('PiEMOS' + str(self.server.number) + '/ConfigFeedback',
                feedback)

    def publish(self, topic, msg):
        self.server.publish(topic, msg)

class PiEMOSReceiver(SocketServer.UDPServer):

    def __init__(self, lc, in_addr, number):
        print('Listening on address', in_addr)
        SocketServer.UDPServer.__init__(self, in_addr, PiEMOSHandler)
        self.lcm = lc
        self.number = number;

    def publish(self, topic, msg):
        self.lcm.publish(topic, msg.encode())

remote_base_address = '10.20.34.10{}'
remote_base_port = 6000
local_base_port = 6000


def main():
    lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=1')
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-port', type=int, action='store')
    parser.add_argument('--remote-port', type=int, action='store')
    parser.add_argument('--remote-address', type=str, action='store')
    parser.add_argument('--number', type=int, action='store')
    args = parser.parse_args()
    vals = [args.remote_address, args.remote_port, args.local_port]
    if any(vals) and not all(vals):
        print('Missing an argument')
        print('Should have remote-address, local-address, and local-port')
        print('Alternatively, only pass number')
        return
    if args.number is not None:
        args.local_port = local_base_port + args.number
        args.remote_port = remote_base_port + args.number
        args.remote_address = remote_base_address.format(args.number)
    bridge = PiEMOSBridge((args.remote_address, args.remote_port), args.number, lc)
    bridge.start()
    piemos_receiver = PiEMOSReceiver(lc, ('', args.local_port), args.number).serve_forever()


if __name__ == '__main__':
    main()
