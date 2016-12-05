#!/usr/bin/env python

import sys, requests, json, csv
from config import config

reader = csv.DictReader(open(sys.argv[2],"r"), delimiter='\t')

url = "{}/UDF/new".format(config["SCRIPT"]["HOST"])
data = { "api_key": config["SCRIPT"]["KEY"], "context": "PEOPLE", "category": sys.argv[1] }
order = 1000
for col in reader.fieldnames:
    print "COL: {}".format(col),

    data["name"] = col.upper()
    data["order"] = order
    r = json.loads(requests.get(url, data=data).text)
    if r["success"]==1:
        print "+"
    else:
        print "-"
    order += 1

for row in reader:
    tmp = row["Join Date"].split("/")
    if len(tmp) == 3: row["Join Date"] = "{}-{}-{}".format(tmp[2],tmp[0].zfill(2),tmp[1].zfill(2))

    tmp = row["Trial Ends"].split("/")
    if len(tmp) == 3: row["Trial Ends"] = "{}-{}-{}".format(tmp[2],tmp[0].zfill(2),tmp[1].zfill(2))

    pid = None
    url = "{}/PEOPLE/new".format(config["SCRIPT"]["HOST"])
    data = { "api_key": config["SCRIPT"]["KEY"], "email": row["Email"] }
    print "Adding {}".format(row["Email"]),
    r = json.loads(requests.get(url, data=data).text)
    if r["success"] == 1:
        pid = r["value"]
        print pid, 
    else:
        url = "{}/PEOPLE/list".format(config["SCRIPT"]["HOST"])
        data = { "api_key": config["SCRIPT"]["KEY"], "query": "PEOPLE_EMAIL={}".format(row["Email"]) }
        print "\nQuerying {}".format(row["Email"]),
        r = json.loads(requests.get(url, data=data).text)
        if r["success"] == 1 and r["data"] and len(r["data"]) > 0:
            pid = r["data"][0]["PEOPLE_ID"]
            print pid,

    print "\t",

    if pid:
        url = "{}/PEOPLE/save".format(config["SCRIPT"]["HOST"])
        data = { "api_key": config["SCRIPT"]["KEY"], "rowid": pid }

        data["col"] = "PEOPLE_NAME_FIRST"
        data["val"] = row["First Name"].upper()
        r = json.loads(requests.get(url, data=data).text)
        print r["success"],

        data["col"] = "PEOPLE_NAME_LAST"
        data["val"] = row["Last Name"].upper()
        r = json.loads(requests.get(url, data=data).text)
        print r["success"],

        data["col"] = "MEMBERSHIP"
        data["val"] = row["Class"].upper()
        r = json.loads(requests.get(url, data=data).text)
        print r["success"],

        for col in reader.fieldnames:
            url = "{}/PEOPLE/save".format(config["SCRIPT"]["HOST"])
            data["col"] = col.upper()
            data["val"] = row[col].upper()
            if data["val"] == "TRUE": data["val"] = 1
            if data["val"] == "Active": data["val"] = 1
            if data["val"] == "Inactive": data["val"] = 0
            r = json.loads(requests.get(url, data=data).text)
            print r["success"],
            if r["success"] == 0:
                print
                print data["col"], data["val"], r["message"]

    print ""
