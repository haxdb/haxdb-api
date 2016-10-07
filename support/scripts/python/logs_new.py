#!/usr/bin/env python

import requests, json
from config import config

data = { "api_key": config["SCRIPT"]["KEY"] }

url = "%s/PEOPLE/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s %s" % (p["PEOPLE_ID"], p["FIRST_NAME"], p["LAST_NAME"])

print ""
people_id = raw_input("Enter PEOPLE_ID: ")
print ""

#####################################################################################################

url = "%s/ASSETS/list" % config["SCRIPT"]["HOST"]
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
        print "%s) %s \t [%s]" % (p["ASSETS_ID"], p["ASSETS_NAME"], p["ASSETS_LOCATION_NAME"])

print ""
assets_id = raw_input("Enter ASSETS_ID: ")
print ""

#####################################################################################################

url = "%s/LIST_ITEMS/list" % config["SCRIPT"]["HOST"]
data["lists_name"] = "LOG ACTIONS"
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s" % (p["LIST_ITEMS_ID"], p["LIST_ITEMS_VALUE"])

print ""
actions_id = raw_input("Enter ACTION_ID: ")
print ""

#####################################################################################################

url = "%s/LIST_ITEMS/list" % config["SCRIPT"]["HOST"] 
data["lists_name"] = "LOG NODES"
r = json.loads(requests.get(url, data=data).text)

for p in r["rows"]:
    print "%s) %s" % (p["LIST_ITEMS_ID"], p["LIST_ITEMS_VALUE"])

print ""
nodes_id = raw_input("Enter NODE_ID: ")
print ""

#####################################################################################################

url = "%s/LOGS/new" % config["SCRIPT"]["HOST"]
data["assets_id"] = assets_id
data["actions_id"] = actions_id
data["people_id"] = people_id
data["nodes_id"] = nodes_id
data["description"] = raw_input("Description: ")
r = json.loads(requests.get(url, data=data).text)

print r
