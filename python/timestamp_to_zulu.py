#!/usr/bin/python3
"""Take unix timestamp on command line and convert to Zulu time

"""

import sys
from datetime import datetime

d = datetime.utcfromtimestamp(int(sys.argv[1])/1000)
zulutime = d.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
print(zulutime)
