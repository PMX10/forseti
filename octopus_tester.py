#!/usr/bin/env python2.7
from __future__ import print_function

import socket
import time
import json

in_addr = ('localhost', 1921)
out_addr = ('localhost', 1922)

confirm_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

health_recvr = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
health_recvr.bind(in_addr)

while True:
    time.sleep(0.001)
    msg = health_recvr.recv(4096)
    print('Received', msg)
    try:
        obj = json.loads(msg)
        confirm = json.dumps({
            'Type':'Confirm',
            'Packet':obj
            })
        confirm_send.sendto(confirm, out_addr)
    except Exception as e:
        print('Exception', e)
        pass
