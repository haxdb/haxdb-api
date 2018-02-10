import requests
import json
import logging
import sys


class hdbAsset:
    host = "http://localhost:8081/v1"
    api_key = None
    meta = {}

    def api(self, call, data=None):
        url = self.host.rstrip("/") + "/" + call.lstrip("/")
        if not data:
            data = {}
        if "api_key" not in data:
            data["api_key"] = self.api_key
        try:
            r = requests.get(url, json=data)
            r = json.loads(r.text)
        except Exception:
            return False
        return r

    def register(self, rfid, sensors):
        data = {
            "rfid": rfid,
            "sensors": sensors,
        }
        r = self.api("ASSETNODES/register", data)
        if r["success"] == 1 and r["api_key"]:
            self.api_key = r["api_key"]
        return r

    def pulse(self, rfid, sensors):
        data = {
            "rfid": rfid,
            "sensors": sensors,
        }
        r = self.api("ASSETNODES/pulse", data)
        return r

    def sense(self, sensors):
        data = {
            "sensors": sensors,
        }
        r = self.api("ASSETNODES/sense", data)
        return r

    def auth(self, rfid):
        data = {
            "rfid": rfid,
        }
        r = self.api("ASSETNODES/auth", data)
        return r



if __name__ == "__main__":
    def getVal(s):
        val = None
        while not val:
            val = raw_input(s)
        return val

    def getSensors():
        i = 0
        sensors = []
        val = raw_input("sensor0: ")
        while val:
            i += 1
            sensors.append(val)
            val = raw_input("sensor{}: ".format(i))
        return sensors


    def getSensorVals():
        i = 0
        sensors = {}
        s = raw_input("sensor0: ")
        while s:
            v = getVal("   val{}: ".format(i))
            i += 1
            sensors[s] = v
            s = raw_input("sensor{}: ".format(i))
        return sensors


    def getKey(hdb):
        hdb.api_key = getVal("API KEY: ")
        return hdb

    def hregister(hdb):
        rfid = getVal("RFID: ")
        sensors = getSensors()
        r = hdb.register(rfid, sensors)
        print r["message"]
        return hdb

    def hpulse(hdb):
        rfid = raw_input("RFID: ")
        sensors = getSensorVals()
        r = hdb.pulse(rfid, sensors)
        print r
        return hdb

    def hsense(hdb):
        sensors = getSensorVals()
        r = hdb.sense(sensors)
        print r
        return hdb

    def hauth(hdb):
        rfid = getVal("RFID: ")
        r = hdb.auth(rfid)
        print r["message"]
        return hdb

    menuoptions = {
        "1": getKey,
        "2": hregister,
        "3": hpulse,
        "4": hsense,
        "5": hauth,
    }

    hdb = hdbAsset()
    while True:
        print "............................."
        print "                             "
        print "    1) API KEY               "
        print "    2) /ASSETNODES/register  "
        print "    3) /ASSETNODES/pulse     "
        print "    4) /ASSETNODES/sense     "
        print "    5) /ASSETNODES/auth      "
        print "                             "
        print "............................."
        which = None
        while which not in menuoptions:
            which = getVal("["+",".join(menuoptions.keys())+"]: ")
            hdb = menuoptions[which](hdb)
        raw_input("[pause]")
