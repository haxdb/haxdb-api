#!/usr/bin/env python

import requests, json
from config import config

data = { }
url = "%s/ASSETS_RFID/pulse?format=min" % config["SCRIPT"]["HOST"]

print "##############################################"
print " LEAVE API KEY BLANK TO GO THROUGH"
print " REGISTRATION PROCESS"
print "##############################################"
print
data["api_key"] = raw_input("API KEY?")

while True:
    print
    data["rfid"] = raw_input("RFID: ")
    r = json.loads(requests.get(url, data=data).text)
    if r and r["value"]:
        data["api_key"] = r["value"]
    
    print "##############################################"    
    print "success: {}".format(r["success"])
    print "message:\n{}".format(r["message"])
    print "##############################################"






