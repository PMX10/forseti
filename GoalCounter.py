#!/usr/bin/env python2.7
import lcm
import threading
import time
import argparse
import os
import os.path
import json

from Forseti import Health
from Forseti import Tag
from Forseti import GoalBoxes

'''
GoalCounter subscribes to GoalReader/Tags and publishes to Goals/Goals.
It counts goals as they appear in goals, and publishes what the goals
should have inside of them.

TODO(ajc): Health, and reset.
'''
class GoalCounter(object):
	def __init__(self, lcm, field_objects):
		self.lcm = lcm
		subscription = self.lcm.subscribe("GoalReader/Tags", self.msg_handler)
		self._read_thread = threading.Thread(target=self._read_loop)
		self._read_thread.daemon = True
		self._write_thread = threading.Thread(target=self._write_loop)
		self._write_thread.daemon = True
		self._health_thread = threading.Thread(target=self._health_loop)
		self._health_thread.daemon = True
		self.startTime = time.time()

		self.goalBoxesLock = threading.Lock()
		self.goalboxes = GoalBoxes()
		self.goalboxes.goals = [[0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0], [0,0,0,0,0]]
		self.readers_to_goals = {'A':0, 'B':1, 'C':2, 'D':3}
		self.field_objects = field_objects

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
	def _write_loop(self):
		while True:
			self.goalBoxesLock.acquire()
			self.lcm.publish("Goals/Goals", self.goalboxes.encode())
			self.goalBoxesLock.release()
			time.sleep(0.1)
	def _health_loop(self):
		while True:
			msg = Health()
			msg.uptime = time.time() - self.startTime
			self.lcm.publish("GoalCounter/Health", msg.encode())
			time.sleep(0.25)

	def msg_handler(self, channel, data):
		if channel == "GoalReader/Tags":
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
					print("object_type=" +  str(self.get_object_type(msg.tagId)))
					self.goalboxes.goals[goal][i] = self.get_object_type(msg.tagId)
					break;
			self.goalBoxesLock.release()

	def get_object_type(self, uid):
		'''
		Returns the object_type of the box associated with the provided uid.
		'''
		for table in self.field_objects:
			if table['tagId'] == unicode(uid):
				return int(table['objectType'])
		return 0 #an unrecognized object has no type

def main():
	print "Starting GoalCounter.py ..."

	lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
	print "LCM Initialized!"
	parser = argparse.ArgumentParser()
	parser.add_argument('--load', type=str, action='store')
	args = parser.parse_args()
	field_file = args.load or 'resources/field_mapping.json'
	field_objects = '[]'
	with open(field_file, 'r') as rfile:
		field_objects = rfile.read()

	field_table = json.loads(field_objects)

	gc = GoalCounter(lc, field_table)
	gc.health_start()
	gc.write_start()
	gc.read_run()

if __name__ == '__main__':
	main()