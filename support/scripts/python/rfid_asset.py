#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

print ""
rfid = raw_input("RFID: ")

data["rfid"] = rfid
url = "%s/RFID_ASSETS/auth" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

print
print r["message"]

if int(r["success"]) == 1:
    print r["row"]["ASSETS_NAME"]
    print "%s %s" % (r["row"]["PEOPLE_FIRST_NAME"], r["row"]["PEOPLE_LAST_NAME"])



