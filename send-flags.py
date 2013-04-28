#!/usr/bin/env python2.7
import lcm
import time

#from exlcm import example_t
import Forseti


lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")



# msg = Forseti.VideoShow()
# msg.ShowFlags = True
# msg.ShowTimer = True
# msg.ShowScore = True
# msg.ShowShroud = False
# msg.ShowSchedule = True
# lc.publish('Video/Show', msg.encode())

'''
msg = Forseti.VideoVersusText()
msg.LeftAllianceText = "leftalliancetext"
msg.RightAllianceText = "rightalliancetext"
msg.MatchText = "matchtext"
lc.publish('Video/VersusText', msg.encode())
'''

msg = Forseti.GoalBoxes()
msg.goals = [
    [1,1,1,1,1],
    [1,1,1,1,1],
    [1,1,1,1,1],
    [1,1,1,1,1]
    ]
lc.publish("Goals/Goals", msg.encode())


# msg = Forseti.Score()
# msg.blue_boxpoints = 10
# msg.gold_boxpoints = 20
# lc.publish("ScoreKeeper/Score", msg.encode())
