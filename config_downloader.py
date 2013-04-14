#!/usr/bin/env python2.7
from __future__ import print_function

import urllib
import json

for i in range(32):
    print('Getting', i)
    target_base = 'https://pioneers.berkeley.edu/team_config/api/{}/'
    #urllib.urlretrieve(target_base.format(i), str(i))
    try:
        f = urllib.urlopen(target_base.format(i))
        obj = json.load(f)
        with open(str(i), 'w') as wfile:
            wfile.write(obj[u'file_contents'])
    except Exception as ex:
        print("Couldn't query", target_base.format(i), "got", ex)
