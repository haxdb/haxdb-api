#!/usr/bin/env python

import requests, json
from config import config

data = { }

rfid = raw_input("RFID: ")
data["rfid"] = rfid

url = "%s/ASSETS_RFID/pulse" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

print
print r["success"]
print r["message"]



