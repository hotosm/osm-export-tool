import boto3
import datetime
import urllib2
import re
import subprocess

client = boto3.client('cloudwatch','us-east-1')
now = datetime.datetime.now()

f = urllib2.urlopen(urllib2.Request('http://localhost/api/timestamp'))
timestamp_str = f.read().split('\n')[0]
parsed = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
# note: this assumes the system time is UTC, because overpass timestamp is UTC
replication_seconds_behind = (now - parsed).seconds

f = urllib2.urlopen(urllib2.Request('http://localhost/api/status'))
match = re.match("(\d+) slots available now",f.read().split('\n')[3])
slots_available = int(match.groups()[0])

pct = subprocess.check_output(['df','--output=pcent','/mnt'])
match = re.match(" (\d+)%",pct.split('\n')[1])
disk_usage_percent = int(match.groups()[0])

client.put_metric_data(
    Namespace='overpass_api',
    MetricData=[
        {
            'MetricName': 'replicationSecondsBehind',
            'Timestamp': now,
            'Value': replication_seconds_behind,
            'Unit':'Seconds'
        },
        {
            'MetricName': 'diskUsagePercent',
            'Timestamp': now,
            'Value': disk_usage_percent,
            'Unit':'Percent'
        },
        {
            'MetricName': 'slotsAvailable',
            'Timestamp': now,
            'Value': slots_available,
            'Unit':'Count'
        }
    ]
)
