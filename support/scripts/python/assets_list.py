#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

url = "%s/ASSETS/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s \t [%s]" % (p["ASSETS_ID"], p["ASSETS_NAME"], p["ASSETS_LOCATION"])


