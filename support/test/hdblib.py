import requests
import json


class hdbapi:
    debug = False
    host = "http://localhost:8081/v1"
    api_key = None

    def api(self, call, data=None):
        url = self.host.rstrip("/") + "/" + call.lstrip("/")
        if not data:
            data = {}
        if "api_key" not in data:
            data["api_key"] = self.api_key

        r = json.loads(requests.get(url, data=data).text)

        if self.debug:
            print "############################"
            print "CALL: {}".format(call)
            print "DATA: {}".format(data)
            print "----------------------------"
            print r
            print "############################"

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


if __name__ == "__main__":
    hdb = hdbapi()
    hdb.debug = False
    print "###########################"
    print ""
    print "\t1) Email"
    print "\t2) API Key"
    print ""
    print "###########################"
    which = None
    while which not in ('1', '2'):
        which = raw_input("1 or 2? ")
    if which == '2':
        hdb.api_key = raw_input("api_key? ")
    else:

        email = raw_input("Email? ")
        while not hdb.auth_email(email):
            email = raw_input("Email? ")

        token = raw_input("Token? ")
        while not hdb.authtoken(token):
            token = raw_input("Token? ")

    print "############################################"
    print hdb.api("PEOPLE/list")["data"]
    print "############################################"
    person = {
        "PEOPLE_EMAIL": "test1@serpco.com",
        "PEOPLE_NAME_FIRST": "FNAME1",
        "PEOPLE_NAME_LAST": "LNAME1"
    }
    print hdb.api("PEOPLE/new", data=person)
    print "############################################"
    person = {
        "PEOPLE_EMAIL": "test2@serpco.com",
        "PEOPLE_NAME_FIRST": "FNAME2",
        "PEOPLE_NAME_LAST": "LNAME2"
    }
    print hdb.api("PEOPLE/new", data=person)
    print "############################################"
    print hdb.api("PEOPLE/list")["data"]
