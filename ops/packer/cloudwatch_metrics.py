#!/usr/bin/python3
import shutil
import boto3

disk_usage = shutil.disk_usage('/mnt/data')
disk_used_percent = disk_usage.used / disk_usage.total * 100
print('DiskUsedPercent {0}'.format(disk_used_percent))

boto3.client('cloudwatch','us-east-1').put_metric_data(
    Namespace="ExportTool",
    MetricData=[
        {
            'MetricName':'DiskUsedPercent',
            'Value':disk_used_percent,
            'Unit':'Percent'

        }
    ])