#!/usr/bin/env python2.7
import lcm
import time

#from exlcm import example_t
import Forseti
from httplib2 import Http
import json


lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

msg = Forseti.Score()
msg.gold_finalscore = -5
msg.blue_finalscore = 10
lc.publish('ScoreKeeper/Score', msg.encode())

'''

http = Http()
resp = http.request('https://pioneers.berkeley.edu/match_schedule/api/match/6/',
                    'POST', body=json.dumps({"alliance1":
                     {"number":1,
                      "autonomous":0,
                      "bonus":2,
                      "manual":2,
                      "penalty":0,
                      "team1":{"number":13,
                               "disqualifed":False},
                      "team2":{"number":12,
                               "disqualified":False}},
                     "alliance2":{
                      "number":2,
                      "autonomous":-10,
                      "bonus":0,
                      "manual":0,
                      "penalty":0,
                      "team1":{
                          "number":8,
                          "disqualified":False},
                      "team2":{
                          "number":29,
                          "disqualified":False}}}),
                    headers={'Content-Type': 'application/json'})

print(resp[1])
f = open('result.html','w')
f.write(resp[1])
f.close()


'''
