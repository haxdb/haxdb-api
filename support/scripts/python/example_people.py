#!/usr/bin/env python

import requests
import json
from config import config

data = {
        "api_key": config["SCRIPT"]["KEY"]
       }

url = "{}/PEOPLE/list".format(config["SCRIPT"]["HOST"])
r = json.loads(requests.get(url, data=data).text)

for p in r["data"]:
    print "{}) {} {}".format(p["PEOPLE_ID"],
                             p["PEOPLE_NAME_FIRST"],
                             p["PEOPLE_NAME_LAST"])
