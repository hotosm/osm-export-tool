import json
import pprint
import logging
from hdx.configuration import Configuration
from hdx.data.dataset import Dataset
import requests
import os

pp = pprint.PrettyPrinter(indent=4)
#Configuration.create(hdx_site='prod',hdx_key=os.environ['HDXKEY'])
#d = Dataset.read_from_hdx('brandon-test-hot-export')
#pp.pprint(d.get_gallery())

headers = {
            'Authorization':os.environ['HDXKEY'],
            'Content-type':'application/json'
        }

data = {
            'id':'bdon-hot-openstreetmap-gin'
        }
data = json.dumps(data)
resp = requests.post('https://data.humdata.org/api/action/package_show',headers=headers,data=data)
for r in resp.json()['result']['resources']:
    pp.pprint(r)
