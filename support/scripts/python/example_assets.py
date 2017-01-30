#!/usr/bin/env python

import requests
import json
from config import config

data = {
        "api_key": config["SCRIPT"]["KEY"]
       }

url = "{}/ASSETS/list".format(config["SCRIPT"]["HOST"])
r = json.loads(requests.get(url, data=data).text)

for p in r["data"]:
    print "{}) {} [{}]".format(p["ASSETS_ID"],
                               p["ASSETS_NAME"],
                               p["ASSETS_LOCATION"])
