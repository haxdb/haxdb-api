#!/usr/bin/env python

import requests, json
from config import config

data = { }

rfid = raw_input("RFID: ")
data["rfid"] = rfid

url = "%s/RFID/asset/register" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

print
print r



