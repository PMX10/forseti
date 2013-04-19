#!/usr/bin/env python2.7
import lcm
import threading
import time

from Forseti import Health
from Forseti import Tag
from Forseti import GoalBoxes
from Forseti import Flags

'''
Flagger subscribes to Goals/Goals and publishes to MaestroDriver/Flags to visualize it.

TODO(ajc): health
'''
class Flagger(object):

    def __init__(self, lcm):
        self.lcm = lcm
        subscription = self.lcm.subscribe("Goals/Goals", self.msg_handler)
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._write_thread = threading.Thread(target=self._write_loop)
        self._write_thread.daemon = True
        self._health_thread = threading.Thread(target=self._health_loop)
        self._health_thread.daemon = True
        self.startTime = time.time()
        self.flagsLock = threading.Lock()
        self.flags = Flags()
        self.flags.goals = [[0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0]]
        self.boxvalsToFlagPos = {0:0, 1:1, 2:-1}

    def read_run(self):
        self._read_thread.run()

    def write_start(self):
        self._write_thread.start()

    def health_start(self):
        self._health_thread.start()

    def _read_loop(self):
        try:
            while True:
                self.lcm.handle()
        except:
            pass

    def _health_loop(self):
        while True:
            msg = Health()
            msg.uptime = time.time() - self.startTime
            self.lcm.publish("Flagger/Health", msg.encode())
            time.sleep(0.25)

    def _write_loop(self):
        while True:
            self.flagsLock.acquire()
            self.lcm.publish("MaestroDriver/Flags", self.flags.encode())
            #self.lcm.publish("Goals/Goals", self.goalboxes.encode())
            self.flagsLock.release()
            time.sleep(0.1)

    def msg_handler(self, channel, data):

        if channel == "Goals/Goals":
            msg = GoalBoxes.decode(data)
            print ("received Goals!")
#            print("reader=" + msg.reader)
#            print("tagId="  + str(msg.tagId))

            # add to goalboxes
            self.flagsLock.acquire()
            for goal in range(0, 4):
                for box in range(0, 5):
                    val = msg.goals[goal][box]
                    print("received goal=" + str(goal) + ", box=" + str(box) + ", value=" + str(val))
                    self.flags.goals[goal][box] = self.boxvalsToFlagPos[val]

            self.flagsLock.release()



def main():
    print "Starting Flagger.py ..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    gc = Flagger(lc)
    gc.health_start()
    gc.write_start()
    gc.read_run()

if __name__ == '__main__':
    main()
