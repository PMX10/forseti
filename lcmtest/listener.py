#!/usr/bin/env python2.7
import lcm

from exlcm import example_t

def my_handler(channel, data):
    msg = example_t.decode(data)
    print("Received message on channel \"%s\"" % channel)
    print("   timestamp   = %s" % str(msg.timestamp))
    print("   position    = %s" % str(msg.position))
    print("   orientation = %s" % str(msg.orientation))
    print("   ranges: %s" % str(msg.ranges))
    print("   name        = '%s'" % msg.name)
    print("   enabled     = %s" % str(msg.enabled))
    print("")

print "Starting LCM Listener..."
lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
print "LCM Initialized!"
subscription = lc.subscribe("EXAMPLE", my_handler)

try:
    while True:
        lc.handle()
except KeyboardInterrupt:
    pass

lc.unsubscribe(subscription)
