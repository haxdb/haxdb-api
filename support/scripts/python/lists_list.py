#!/usr/bin/env python

import requests, json
from config import config

url = "%s/LISTS/list" % config["SCRIPT"]["HOST"]

data = { "api_key": config["SCRIPT"]["KEY"] }
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s" % (p["LISTS_ID"], p["LISTS_NAME"])

print ""
listid = raw_input("Enter LISTS_ID: ")
print ""

url = "%s/LIST_ITEMS/list/%s" % (config["SCRIPT"]["HOST"], listid)
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s \t %s" % (p["LIST_ITEMS_ID"], p["LIST_ITEMS_VALUE"], p["LIST_ITEMS_DESCRIPTION"])


