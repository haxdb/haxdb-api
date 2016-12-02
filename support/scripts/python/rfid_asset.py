#!/usr/bin/env python

import requests, json
from config import config

url = "%s/ASSETS_RFID/pulse" % config["SCRIPT"]["HOST"]
data = { "api_key": config["SCRIPT"]["KEY"] }

while True:
    data["rfid"] = raw_input("RFID: ")
    r = json.loads(requests.get(url, meta=meta).text)

    print "###################################"
    print r["success"]
    print r["message"]
    print "###################################"



