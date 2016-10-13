#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

data["lists_name"] = "LOG ACTIONS"
url = "%s/LIST_ITEMS/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s" % (p["LIST_ITEMS_VALUE"],)

print ""
action = raw_input("ACTION: ")
print ""
rfid = raw_input("RFID: ")

data["rfid"] = rfid
data["action"] = action
url = "%s/RFID/asset/auth" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

print
print r["message"]

if int(r["success"]) == 1:
    print r["row"]["ASSETS_NAME"]
    print "%s %s" % (r["row"]["PEOPLE_FIRST_NAME"], r["row"]["PEOPLE_LAST_NAME"])



