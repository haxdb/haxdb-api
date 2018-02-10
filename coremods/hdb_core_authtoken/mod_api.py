import time
from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/AUTH/token", methods=["GET", "POST"])
    def mod_auth_token():
        now = time.time()
        token = haxdb.get("token")
        dbalist = haxdb.config["AUTHEMAIL"]["DBA"].split(',')
        config_dbas = [x.strip().upper() for x in dbalist]

        person = haxdb.func("AUTHTOKEN:VALIDATE")(token)
        if not person:
            return haxdb.response(success=0, message=person)

        pname = "{} {}".format(person["PEOPLE_NAME_FIRST"],
                               person["PEOPLE_NAME_LAST"])
        nname = "{} TOKEN AUTH".format(pname)

        ip = str(request.access_route[-1])
        expire = int(haxdb.config["AUTHTOKEN"]["TOKEN_EXPIRE"])+now
        dba = person["PEOPLE_DBA"]
        if person["PEOPLE_EMAIL"].upper() in config_dbas:
            dba = 1

        api_key, nodes_id = haxdb.func("NODES:CREATE")(nname, ip, expire, dba,
                                                 people_id=person["PEOPLE_ID"])

        raw = {
            "api_key": api_key,
            "name": pname,
        }
        return haxdb.response(success=1, message="AUTHENTICATED", raw=raw)
