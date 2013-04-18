#!/usr/bin/env python2.7
import lcm
import threading
import time

from Forseti import Health
from Forseti import Tag
from Forseti import GoalBoxes

class GoalCounter(object):
	def __init__(self, lcm):
		self.lcm = lcm
		subscription = self.lcm.subscribe("GoalReader/Tags", self.msg_handler)
		self._read_thread = threading.Thread(target=self._read_loop)
		self._read_thread.daemon = True
		self._write_thread = threading.Thread(target=self._write_loop)
		self._write_thread.daemon = True
		self.goalBoxesLock = threading.Lock()
		self.goalboxes = GoalBoxes()
		self.goalboxes.goals = [[0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0]]
		self.readers_to_goals = {'A':0, 'B':1, 'C':2, 'D':3}

	def read_run(self):
		self._read_thread.run()

	def write_start(self):
		self._write_thread.start()

	def _read_loop(self):
		try:
			while True:
				self.lcm.handle()
		except:
			pass
	def _write_loop(self):
		while True:
			self.goalBoxesLock.acquire()
			self.lcm.publish("Goals/Goals", self.goalboxes.encode())
			self.goalBoxesLock.release()
			time.sleep(0.1)

	def msg_handler(self, channel, data):
		if (channel == "GoalReader/Tags"):
			msg = Tag.decode(data)
			print ("received tag!")
			print("reader=" + msg.reader)
			print("tagId="  + str(msg.tagId))

			# send response
			self.lcm.publish("GoalReader/TagConfirm", data)
			goal = self.readers_to_goals[msg.reader]
			print "goal=" + str(goal)

			self.goalBoxesLock.acquire()
			# add to goalboxes
			for i in range(0, 5):
				if self.goalboxes.goals[goal][i] is 0:
					self.goalboxes.goals[goal][i] = 1 #todo use mapping
					break;
			self.goalBoxesLock.release()


def main():
	print "Starting GoalCounter.py ..."

	lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
	print "LCM Initialized!"

	gc = GoalCounter(lc)
	gc.write_start()
	gc.read_run()



if __name__ == '__main__':
	main()