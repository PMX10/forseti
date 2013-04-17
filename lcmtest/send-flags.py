import lcm
import time

#from exlcm import example_t
from Forseti import Flags

lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = Flags()
msg.goals = [[1, 0, 0, 3, 4], [1, 0, 0, 3, 4], [1, 0, 0, 3, 4], [1, 0, 0, 3, 4]]

lc.publish("MaestroDriver/Flags", msg.encode())
