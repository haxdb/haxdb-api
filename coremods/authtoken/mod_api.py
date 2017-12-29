import os
import base64
import json
import time
import re
from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/AUTHTOKEN", methods=["GET", "POST"])
    @haxdb.route("/AUTHTOKEN/<token>", methods=["GET", "POST"])
    def mod_auth_token(token=None):
        token = token or haxdb.get("token")
        dbas = [x.strip().upper() for x in config["AUTH"]["DBA"].split(',')]
        now = int(time.time())

        # DELETE OLD TOKEN
        db.query("DELETE FROM AUTH_TOKEN WHERE AUTH_TOKEN_EXPIRE<%s", (now,))
        if db.error:
            return haxdb.output(success=0, message=db.error, meta=meta)
        db.commit()

        # VALIDATE TOKEN
        sql = """
        SELECT *
        FROM AUTH_TOKEN
        JOIN PEOPLE ON AUTH_TOKEN_PEOPLE_ID = PEOPLE_ID
        WHERE
        AUTH_TOKEN_TOKEN = %s
        AND AUTH_TOKEN_EXPIRE > %s
        """
        db.query(sql, (token, now,))
        row = db.next()
        if not row:
            msg = "TOKEN IS INVALID OR EXPIRED.\nLOG IN AGAIN."
            return haxdb.response(success=0, message=msg)

        # CREATE SESSION NODE
        api_key = base64.urlsafe_b64encode(os.urandom(500))[5:39]
        expire = int(time.time() + int(config["AUTH"]["TOKEN_EXPIRE"]))
        node_name = "{} {} TOKEN AUTH".format(row["PEOPLE_NAME_FIRST"],
                                              row["PEOPLE_NAME_LAST"],)
        dba = row["PEOPLE_DBA"]
        if row["PEOPLE_EMAIL"].upper() in config_dbas:
            dba = 1
        ip = str(request.access_route[-1])
        sql = """
        INSERT INTO NODES (NODES_API_KEY,NODES_PEOPLE_ID,NODES_NAME,
                           NODES_READONLY,NODES_DBA,NODES_IP,NODES_EXPIRE,
                           NODES_ENABLED,NODES_QUEUED)
        VALUES (%s,%s,%s,0,%s,%s,%s,1,0)
        """
        db.query(sql, (api_key, row["PEOPLE_ID"], node_name, dba, ip, expire,))
        if db.error:
            return haxdb.output(success=0, message=db.error, meta=meta)

        # REMOVE TOKEN
        sql = "DELETE FROM AUTH_TOKEN WHERE AUTH_TOKEN_TOKEN=%s"
        db.query(sql, (token,))
        if db.error:
            return haxdb.output(success=0, message=db.error, meta=meta)
        db.commit()

        meta["people_name"] = "{} {}".format(row["PEOPLE_NAME_FIRST"],
                                             row["PEOPLE_NAME_LAST"])
        return haxdb.output(success=1,
                            message="AUTHENTICATED",
                            meta=meta,
                            value=api_key)
