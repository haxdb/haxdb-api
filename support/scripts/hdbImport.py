import requests
import json
import sys
import csv


class hdbImport:
    host = "http://localhost:8081/v1"
    apiKey = None
    metaData = {}
    apiData = {}
    listData = {}
    oldIdMap = {}

    def __init__(self, apiHost=None, apiKey=None):
        self.host = apiHost
        self.apiKey = apiKey
        self.meta()

    def api(self, call, data=None, stream=False):
        url = self.host.rstrip("/") + "/" + call.lstrip("/")
        if not data:
            data = {}
        if "apiKey" not in data:
            data["api_key"] = self.apiKey
        try:
            r = requests.get(url, json=data, stream=stream)
            r = json.loads(r.text)
        except Exception:
            return False
        return r

    def cacheMap(self, apiname):
        r = self.api("/{}/list".format(apiname))
        if r:
            self.apiData[apiname] = {}
            for row in r["data"]:
                self.apiData[apiname][row["ROWNAME"]] = row["ROWID"]

    def meta(self):
        r = self.api("/META")
        if r:
            self.metaData = r
            for l in r["lists"]:
                self.listData[l] = {}
                for li in r["lists"][l]:
                    self.listData[l][li["value"]] = li["name"]
        return r

    def importStep1(self, apiname):
        # STEP 1: cache and map apis from id cols
        if apiname not in h.metaData["mods"]:
            return False

        cols = self.metaData["mods"][apiname]["COLS"]
        for col in cols:
            if col["TYPE"] == "ID":
                self.cacheMap(col["ID_API"])

        return True

    def checkReqVals(self, cols, row):
        for col in cols:
            if col["REQUIRED"] == 1:
                val = row[col["NAME"]]
                if col["TYPE"] == "ID":
                    idapi = col["ID_API"]
                    if idapi not in self.apiData:
                        msg = "REQUIRED COL {} REFERENCES UNKNOWN API {}"
                        msg = msg.format(col["NAME"], idapi)
                        print msg
                        return False
                    if val not in self.apiData[idapi]:
                        msg = "REQUIRED COL {} REFERENCING API {} "
                        msg += "USES UNKNOWN VALUE {}"
                        msg = msg.format(col["NAME"], idapi, val)
                        print msg
                        return False
                elif col["TYPE"] == "LIST":
                    lname = col["LIST_NAME"]
                    if lname not in self.listData:
                        msg = "REQUIRED COL {} REFERENCES UNKNOWN LIST {}"
                        msg = msg.format(col["NAME"], lname)
                        print msg
                        return False
                    if val not in self.listData[lname]:
                        msg = "REQUIRED COL {} REFERENCING LIST {} "
                        msg += "USES UNKNOWN VALUE {}"
                        msg = msg.format(col["NAME"], lname, val)
                        print msg
                        return False
        return True

    def importStep2(self, apiName, csvFile):
        # STEP 2: Check for invalid id's or list values in required cols
        cols = self.metaData["mods"][apiName]["COLS"]
        reader = csv.DictReader(open(csvFile))
        for row in reader:
            if not self.checkReqVals(cols, row):
                return False
        return True

    def getVal(self, col, val):
        if col["TYPE"] == "ID":
            idapi = col["ID_API"]
            if idapi not in self.apiData or val not in self.apiData[idapi]:
                return None
            return self.apiData[idapi][val]
        elif col["TYPE"] == "LIST":
            lname = col["LIST_NAME"]
            if lname not in self.listData or val not in self.listData[lname]:
                return None
        return val

    def newRequired(self, apiName, cols, row, e):
        newData = {}
        logtxt = ""
        for col in cols:
            if col["REQUIRED"] == 1:
                val = self.getVal(col, row[col["NAME"]])
                newData[col["NAME"]] = val
                logtxt += ",{}={}".format(col["NAME"], val)
        data = {"new": newData}
        print "{}/new: {}".format(apiName, logtxt[1:])
        r = self.api("{}/new".format(apiName), data)
        if r and "success" in r and r["success"] == 1 and "rowid" in r:
            oldId = row["{}_ID".format(apiName)]
            self.oldIdMap[oldId] = r["rowid"]
            return r["rowid"]
        else:
            msg = "UNABLE TO INSERT"
            if "message" in r:
                msg = r["message"]
            edata = {
                "rowid": None,
                "field": None,
                "value": row,
                "reason": msg
                }
            e.writerow(edata)
        return False

    def matchCol(self, cols, cname):
        for col in cols:
            if col["NAME"] == cname or col["HEADER"] == cname:
                return col
        return False

    def saveData(self, rowid, apiName, cols, row, e):
        for cname in row:
            col = self.matchCol(cols, cname)
            if col:
                if col["REQUIRED"] == 1:
                    continue

                if col["TYPE"] == "FILE":
                    continue

                val = self.getVal(col, row[cname])
                saveData = {col["NAME"]: val}
                data = {"save": saveData, "rowid": rowid}
                r = self.api("{}/save".format(apiName), data)
                if not r or "success" not in r or r["success"] != 1:
                    msg = "UNABLE TO SAVE"
                    if r and "message" in r:
                            msg = r["message"]
                            edata = {
                                "rowid": rowid,
                                "field": col["NAME"],
                                "value": val,
                                "reason": msg
                                }
                            e.writerow(edata)
            else:
                msg = "UNMATCHED COLUMN {}".format(cname)
                val = row[cname]
                edata = {
                    "rowid": rowid,
                    "field": cname,
                    "value": val,
                    "reason": msg
                    }
                e.writerow(edata)

    def importStep3(self, apiName, csvFile, excFile):
        # STEP 3: Create new entries with valid data.
        #         Write invalid data to excFile:
        #         [oldid, newid, field, value, reason]

        fieldnames = ["oldid", "rowid", "field", "value", "reason"]
        e = csv.DictWriter(open(excFile, "a"), fieldnames)
        cols = self.metaData["mods"][apiName]["COLS"]
        reader = csv.DictReader(open(csvFile))
        for row in reader:
            r = self.newRequired(apiName, cols, row, e)
            if r:
                self.saveData(r, apiName, cols, row, e)
        return True


if __name__ == "__main__":
    if len(sys.argv) < 6:
        msg = "Usage: {} <apiHost> <apiKey> <apiName> "
        msg += "<csvFile> <excFile> <newidFile>"
        print msg.format(sys.argv[0])
        quit()

    apiHost = sys.argv[1]
    apiKey = sys.argv[2]
    apiName = sys.argv[3]
    csvFile = sys.argv[4]
    excFile = sys.argv[5]
    newidFile = sys.argv[6]

    h = hdbImport(apiHost, apiKey)
    if h.importStep1(apiName):
        if h.importStep2(apiName, csvFile):
            h.importStep3(apiName, csvFile, excFile)

    if h.oldIdMap:
        f = open(newidFile, "w")
        for newid in h.oldIdMap:
            f.write("{}\t{}\n".format(newid, h.oldIdMap[newid]))
        f.close()
