#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

url = "%s/ASSETS/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s \t [%s]" % (p["ASSETS_ID"], p["ASSETS_NAME"], p["ASSETS_LOCATION_NAME"])

print ""
assets_id = raw_input("ASSETS_ID: ")
print ""
rfid = raw_input("RFID: ")

data["assets_id"] = assets_id
data["rfid"] = rfid
url = "%s/RFID/asset" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

print
print r["info"]

if int(r["success"]) == 1:
    print r["row"]["ASSETS_NAME"]
    print "%s %s" % (r["row"]["PEOPLE_FIRST_NAME"], r["row"]["PEOPLE_LAST_NAME"])



