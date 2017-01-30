#!/usr/bin/env python

import requests
import json
from config import config


data = {
        "api_key": config["SCRIPT"]["KEY"]
       }

url = "{}/LISTS/list".format(config["SCRIPT"]["HOST"])
r = json.loads(requests.get(url, data=data).text)

for p in r["data"]:
    print "{}) {}".format(p["LISTS_ID"], p["LISTS_NAME"])

print ""
data["LISTS_ID"] = raw_input("Enter LISTS_ID: ")
print ""

url = "{}/LIST_ITEMS/list".format(config["SCRIPT"]["HOST"])
r = json.loads(requests.get(url, data=data).text)

for p in r["data"]:
    print "{}) {} ({})".format(p["LIST_ITEMS_ID"],
                               p["LIST_ITEMS_VALUE"],
                               p["LIST_ITEMS_DESCRIPTION"])
