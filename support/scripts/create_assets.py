import requests
import json
import logging
import sys
import time


class hdbapi:
    host = "http://localhost:8081/v1"
    api_key = None
    meta = {}

    def api(self, call, data=None):
        url = self.host.rstrip("/") + "/" + call.lstrip("/")
        if not data:
            data = {}
        if "api_key" not in data:
            data["api_key"] = self.api_key

        logging.debug("############################")
        logging.debug("CALL: {}".format(call))
        logging.debug("URL: {}".format(url))
        logging.debug("DATA: {}".format(data))

        try:
            r = requests.get(url, data=data)
            r = json.loads(r.text)
            logging.debug("----------------------------")
            logging.debug(r)
        except requests.exceptions.RequestException as e:
            logging.warn(e)
            return False
        except ValueError:
            print r
            return False

        logging.debug("############################")

        return r

    def auth_email(self, email):
        r = self.api("AUTH/email", {"email": email})
        if r["success"] == 1:
            return True
        return False

    def authtoken(self, token):
        r = self.api("AUTH/token", {"token": token})
        if r["success"] != 1:
            return False
        self.api_key = r["api_key"]
        return True

    def meta(self):
        r = self.api("META")
        if r and r["success"] == 1:
            print r
            self.meta = r["data"]
            return True
        return False

if __name__ == "__main__":
    from tabulate import tabulate
    from pprint import pprint
    hdb = hdbapi()
    #logging.basicConfig(level=logging.DEBUG)
    print "..........................."
    print ""
    print "    1) Email"
    print "    2) API Key"
    print ""
    print "..........................."
    which = None
    while which not in ('1', '2'):
        which = raw_input("1 or 2? ")
    print "..........................."
    if which == '2':
        hdb.api_key = raw_input("api_key? ")
        print "..........................."
    else:

        email = raw_input("Email? ")
        while not hdb.auth_email(email):
            email = raw_input("Email? ")
        print "..........................."

        token = raw_input("Token? ")
        while not hdb.authtoken(token):
            token = raw_input("Token? ")
        print "..........................."
        print hdb.api_key
        print "..........................."

    for i in range(356,10000):
        aname = "ASSET{}".format(i)
        atype = "WIDGET{}".format(i)
        data = {
            "new[ASSETS_NAME]": aname,
            "new[ASSETS_TYPE]": atype,
        }
        r = hdb.api("ASSETS/new", data)
        if r["success"] != 1:
            print r["message"]
        time.sleep(.025)
