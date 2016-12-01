#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

url = "%s/PEOPLE/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s %s" % (p["PEOPLE_ID"], p["PEOPLE_NAME_FIRST"], p["PEOPLE_NAME_LAST"])


