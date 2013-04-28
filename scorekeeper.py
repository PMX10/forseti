#!/usr/bin/env python2.7
import lcm
import threading
import time

from Forseti import *


class ScoreKeeper(object):

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
        self.scorelock = threading.Lock()
        self.score = Score()
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
            self.lcm.publish("ScoreKeeper/Health", msg.encode())
            time.sleep(0.25)

    def _write_loop(self):
        while True:
            self.scorelock.acquire()
            self.lcm.publish("ScoreKeeper/Score", self.score.encode())
            self.scorelock.release()
            time.sleep(0.1)

    def msg_handler(self, channel, data):

        if channel == "Goals/Goals":
            msg = GoalBoxes.decode(data)
            print ("received Goals!")
#            print("reader=" + msg.reader)
#            print("tagId="  + str(msg.tagId))

            # add to goalboxes
            self.scorelock.acquire()
#            print("score=" + str(score.blue_boxpoints))
#            print("type=" + str(type(score.blue_boxpoints)))
            self.score.blue_boxpoints = 0
            self.score.gold_boxpoints = 0

            for goal in range(0, 4):
                cur_score = 0
                for box in range(4, -1, -1):
                    val = msg.goals[goal][box]
                    if val == 1:
                        cur_score = cur_score + 2
                    elif val == 2:
                        cur_score = cur_score * 2
                print("cur_score=" + str(cur_score))
                if (goal % 2 == 0):
                    self.score.gold_boxpoints = self.score.gold_boxpoints + cur_score
                    print("adding to gold score, score=" + str(self.score.gold_boxpoints))
                else :
                    self.score.blue_boxpoints = self.score.blue_boxpoints + cur_score
                    print("adding to blue score, score=" + str(self.score.blue_boxpoints))
            self.score.blue_finalscore = self.score.blue_boxpoints - self.score.blue_penalties
            self.score.gold_finalscore = self.score.gold_boxpoints - self.score.gold_penalties
            print("gold=" + str(self.score.gold_finalscore) + ",\t blue=" + str(self.score.blue_finalscore))
            self.scorelock.release()


def main():
    print "Starting scorekeeper.py ..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    sk = ScoreKeeper(lc)
    sk.health_start()
    sk.write_start()
    sk.read_run()

if __name__ == '__main__':
    main()
