#!/usr/bin/env python2.7
import lcm
import threading
import time
import Forseti

class VersusWriter(object):

    def __init__(self, lcm):
        self.lcm = lcm
        subscription = self.lcm.subscribe("Match/Init", self.msg_handler)
        self._read_thread = threading.Thread(target=self._read_loop)
        self._read_thread.daemon = True
        self._write_thread = threading.Thread(target=self._write_loop)
        self._write_thread.daemon = True
        self._health_thread = threading.Thread(target=self._health_loop)
        self._health_thread.daemon = True
        self.startTime = time.time()
        self.versus_text_lock = threading.Lock()
        self.versusText = Forseti.VideoVersusText()
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
            msg = Forseti.Health()
            msg.uptime = time.time() - self.startTime
            self.lcm.publish("VersusWriter/Health", msg.encode())
            time.sleep(0.25)

    def _write_loop(self):
        while True:
            self.versus_text_lock.acquire()
            self.lcm.publish("Video/VersusText", self.versusText.encode())
            self.versus_text_lock.release()
            time.sleep(1.0)

    def msg_handler(self, channel, data):
        print("received Match!")
        msg = Forseti.Match.decode(data)
        self.versus_text_lock.acquire()

        self.versusText.RightAllianceText = (
            str(msg.team_numbers[0]) + ":" +
            str(msg.team_names[0]) +
            "\n" +
            str(msg.team_numbers[1]) + ":" +
            str(msg.team_names[1]))

        self.versusText.LeftAllianceText = (
            str(msg.team_numbers[2]) + ":" +
            str(msg.team_names[2]) +
            "\n" +
            str(msg.team_numbers[3]) + ":" +
            str(msg.team_names[3]))

        self.versusText.MatchText = "Match " + str(msg.match_number)
        self.versus_text_lock.release()

def main():
    print "Starting video_versus_writer.py ..."

    lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
    print "LCM Initialized!"

    gc = VersusWriter(lc)
    gc.health_start()
    gc.write_start()
    gc.read_run()

if __name__ == '__main__':
    main()
