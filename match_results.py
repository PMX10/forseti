#!/usr/bin/env python2.7
from httplib2 import Http
from urllib import urlencode
import json

#response = client.post('/match_schedule/api/match/1/',data)

print "sending test post"

json_dict = {"alliance1":
             {"number":1,
              "autonomous":5,
              "bonus":0,
              "manual":3,
              "penalty":1,
              "team1":{"number":24,
                       "disqualified":False},
              "team2":{"number":14,
                       "disqualified":False}},
             "alliance2":{
              "number":2,
              "autonomous":5,
              "bonus":0,
              "manual":3,
              "penalty":1,
              "team1":{
                  "number":12,
                  "disqualified":False},
              "team2":{
                  "number":22,
                  "disqualified":False}}}
json_data = json.dumps(json_dict)
data = {'data':json_data}
print ("data=" + json.dumps(data))
'''
h = Http()
resp, content = h.request("http://tbp.berkeley.edu:9137/match_schedule/api/match/1", "POST", json_data)
print("response=" + str(resp))
print("content=" + str(content))
'''


http = Http()
resp, content = http.request('https://pioneers.berkeley.edu/match_schedule/api/match/2/','POST', body=json.dumps(data),headers={'Content-Type': 'application/json'})
print ("response=" + str(resp))
print ("content="  + str(content))