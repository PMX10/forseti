#!/usr/bin/env python2.7
import lcm
import threading

from Forseti import Health
from Forseti import Tag

class Flagger(object):
	def __init__(self, lcm):
		self.lcm = lcm
		subscription = self.lcm.subscribe("GoalReader/Tags", self.msg_handler)
		self._thread = threading.Thread(target=self._loop)
		self._thread.daemon = True

	def run(self):
		self._thread.run()

	def _loop(self):
		try:
			while True:
				self.lcm.handle()
		except:
			pass

	def msg_handler(self, channel, data):
		if (channel == "GoalReader/Tags"):
			msg = Tag.decode(data)
			print ("received tag!")
			print("reader=" + msg.reader)
			print("tagId="  + str(msg.tagId))

			# send response
			self.lcm.publish("GoalReader/TagConfirm", data)

def main():
	print "Starting Flagger.py ..."

	lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
	print "LCM Initialized!"

	flagger = Flagger(lc)
	flagger.run()



if __name__ == '__main__':
	main()