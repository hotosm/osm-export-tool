import datadog
from datadog import statsd

import datetime
import urllib2
import re

now = datetime.datetime.now()

f = urllib2.urlopen(urllib2.Request('http://localhost:6080/api/timestamp'))
timestamp_str = f.read().split('\n')[0]
parsed = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
# note: this assumes the system time is UTC, because overpass timestamp is UTC
replication_seconds_behind = (now - parsed).seconds
statsd.gauge("overpass.replication_seconds_behind",replication_seconds_behind)
