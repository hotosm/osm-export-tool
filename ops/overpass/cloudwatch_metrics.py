#!/usr/bin/python3
import datetime
import shutil
import urllib.request as urlrequest
import boto3

disk_usage = shutil.disk_usage('/data')
disk_used_percent = disk_usage.used / disk_usage.total * 100
print('DiskUsedPercent {0}'.format(disk_used_percent))
timestamp = urlrequest.urlopen('http://localhost/api/timestamp').readline().decode('utf-8')
parsed = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ\n")
now = datetime.datetime.now()
replication_seconds_behind = (now - parsed).total_seconds()
print('ReplicationSecondsBehind {0}'.format(replication_seconds_behind))

boto3.client('cloudwatch','us-east-1').put_metric_data(
    Namespace="Overpass",
    MetricData=[
        {
            'MetricName':'ReplicationSecondsBehind',
            'Value':replication_seconds_behind,
            'Unit':'Seconds'
        },
        {
            'MetricName':'DiskUsedPercent',
            'Value':disk_used_percent,
            'Unit':'Percent'

        }
    ])