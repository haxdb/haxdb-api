import time
import base64
import os
from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/AUTH/token", methods=["GET", "POST"])
    def mod_auth_token():
        token = haxdb.get("token")
        dbalist = haxdb.config["AUTHEMAIL"]["DBA"].split(',')
        config_dbas = [x.strip().upper() for x in dbalist]
        now = int(time.time())

        # DELETE OLD TOKEN
        sql = "DELETE FROM AUTHTOKEN WHERE AUTHTOKEN_EXPIRE<%s"
        haxdb.db.query(sql, (now,))
        if haxdb.db.error:
            return haxdb.response(success=0, message=haxdb.db.error)
        haxdb.db.commit()

        # VALIDATE TOKEN
        sql = """
        SELECT *
        FROM AUTHTOKEN
        JOIN PEOPLE ON AUTHTOKEN_PEOPLE_ID = PEOPLE_ID
        WHERE
        AUTHTOKEN_TOKEN = %s
        AND AUTHTOKEN_EXPIRE > %s
        """
        haxdb.db.query(sql, (token, now,))
        row = haxdb.db.next()
        if not row:
            msg = "TOKEN IS INVALID OR EXPIRED.\nLOG IN AGAIN."
            return haxdb.response(success=0, message=msg)

        # CREATE SESSION NODE
        api_key = base64.urlsafe_b64encode(os.urandom(500))[5:39]
        expire = int(haxdb.config["AUTHTOKEN"]["TOKEN_EXPIRE"])
        expire += time.time()
        node_name = "{} {} TOKEN AUTH".format(row["PEOPLE_NAME_FIRST"],
                                              row["PEOPLE_NAME_LAST"],)
        dba = row["PEOPLE_DBA"]
        if row["PEOPLE_EMAIL"].upper() in config_dbas:
            dba = 1
        ip = str(request.access_route[-1])
        sql = """
        INSERT INTO NODES (NODES_API_KEY,NODES_PEOPLE_ID,NODES_NAME,
                           NODES_DBA,NODES_IP,NODES_EXPIRE,
                           NODES_ENABLED)
        VALUES (%s,%s,%s,%s,%s,%s,1)
        """
        params = (api_key, row["PEOPLE_ID"], node_name, dba, ip, expire,)
        haxdb.db.query(sql, params)
        if haxdb.db.error:
            return haxdb.response(success=0, message=haxdb.db.error)

        # REMOVE TOKEN
        sql = "DELETE FROM AUTHTOKEN WHERE AUTHTOKEN_TOKEN=%s"
        haxdb.db.query(sql, (token,))
        if haxdb.db.error:
            return haxdb.response(success=0, message=haxdb.db.error)
        haxdb.db.commit()

        raw = {
            "api_key": api_key,
            "name": "{} {}".format(row["PEOPLE_NAME_FIRST"],
                                   row["PEOPLE_NAME_LAST"])
        }
        return haxdb.response(success=1, message="AUTHENTICATED", raw=raw)
