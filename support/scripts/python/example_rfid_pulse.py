#!/usr/bin/env python

import requests
import json
from config import config

api_key = raw_input("API KEY: ")

url = "{}/ASSETS_RFID/pulse".format(config["SCRIPT"]["HOST"])
while True:
    rfid = raw_input("RFID: ")

    data = {
        "api_key": api_key,
        "rfid": rfid
    }
    t = requests.get(url, data=data).text
    r = json.loads(t)

    s = r["success"]
    msg = r["message"]

    print "{}\n{}".format(s, msg)

    if "value" in r and r["value"]:
        api_key = r["value"]
        print "RECEIVED API KEY\n{}".format(api_key)
