import requests
import json
import sys


class hdbAsset:
    host = "http://localhost:8081/v1"
    api_key = None
    meta = {}

    def __init__(self, host=None):
        if host:
            self.host = host

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
        if r and r["success"] == 1 and r["api_key"]:
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
    import pprint
    pp = pprint.PrettyPrinter(indent=4)

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
        pp.pprint(r)
        return hdb

    def hpulse(hdb):
        rfid = raw_input("RFID: ")
        sensors = getSensorVals()
        r = hdb.pulse(rfid, sensors)
        pp.pprint(r)
        return hdb

    def hsense(hdb):
        sensors = getSensorVals()
        r = hdb.sense(sensors)
        pp.pprint(r)
        return hdb

    def hauth(hdb):
        rfid = getVal("RFID: ")
        r = hdb.auth(rfid)
        pp.pprint(r)
        return hdb

    menuoptions = {
        "1": getKey,
        "2": hregister,
        "3": hpulse,
        "4": hsense,
    }

    if len(sys.argv) > 1:
        hdb = hdbAsset(sys.argv[1])
    else:
        hdb = hdbAsset()
    while True:
        print "............................."
        print "                             "
        print "    1) API KEY               "
        print "    2) /ASSETNODES/register  "
        print "    3) /ASSETNODES/pulse     "
        print "    4) /ASSETNODES/sense     "
        print "                             "
        print "............................."
        which = None
        while which not in menuoptions:
            which = getVal("[1,2,3,4]: ")
        hdb = menuoptions[which](hdb)
        raw_input("[pause]")
