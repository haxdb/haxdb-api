import mod_data
import os
import base64
import json
import time
import datetime
from flask import request, session

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, mod_def):
    global haxdb, db, config
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def run():
    global haxdb, db, config

    @haxdb.app.before_request
    def mod_api_keys_before_request():
        session.permanent = True
        key = haxdb.data.var.get("api_key", use_session=True)

        if key:
            ip = str(request.access_route[-1])
            sql = """
            select *
            from NODES
            where
            NODES_API_KEY=%s
            and NODES_ENABLED='1'
            and (NODES_EXPIRE IS NULL OR NODES_EXPIRE > %s)
            and (NODES_IP IS NULL OR NODES_IP='' OR NODES_IP=%s)
            """
            now = int(time.time())
            db.query(sql, (key, now, ip,))
            row = db.next()
            if row and row["NODES_API_KEY"] == key:
                haxdb.data.session.set("api_authenticated", 1)
                haxdb.data.session.set("api_people_id", row["NODES_PEOPLE_ID"])
                haxdb.data.session.set("nodes_id", row["NODES_ID"])
                haxdb.data.session.set("api_key", row["NODES_API_KEY"])
                haxdb.data.session.set("api_readonly", row["NODES_READONLY"])
                haxdb.data.session.set("api_dba", row["NODES_DBA"])
            else:
                haxdb.data.session.set("api_authenticated", 0)

    @haxdb.app.route("/NODES/list", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_api_keys_list():
        def calc_row(row):
            row["NODES_EXPIRE_VIEW"] = "N/A"
            try:
                row["NODES_EXPIRE_VIEW"] = datetime.datetime.fromtimestamp(
                    row["NODES_EXPIRE"]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
            return row

        sql = "DELETE FROM NODES WHERE NODES_EXPIRE<%s"
        db.query(sql, (time.time(),))
        db.commit()

        sql = """
        SELECT N.*, UDF_NAME, UDF_DATA_VALUE
        FROM (
        SELECT
        NODES.*,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST
        ASSETS_NAME
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        ) N
        """

        return apis["NODES"].list_call(sql=sql, calc_row_function=calc_row)

    @haxdb.app.route("/NODES/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_create():
        is_dba = (haxdb.session.get("api_dba") == 1)
        people_id = haxdb.data.var.get("people_id") or haxdb.session.get("api_people_id")
        dba = haxdb.data.var.get("dba") or '0'
        readonly = haxdb.data.var.get("readonly") or '0'
        expire_seconds = haxdb.data.var.get("expire_seconds")

        meta = {}
        meta["api"] = "NODES"
        meta["action"] = "new"
        meta["people_id"] = people_id
        meta["dba"] = dba
        meta["readonly"] = readonly
        meta["expire_seconds"] = expire_seconds

        if not is_dba:
            people_id = haxdb.session.get("api_people_id")
            dba = 0

        api_key = base64.urlsafe_b64encode(os.urandom(500))[5:260]

        if expire_seconds:
            expire_time = int(time.time()) + int(expire_seconds)
            sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_QUEUED, NODES_EXPIRE)
                    VALUES (%s,%s,%s,%s,'0','0',%s)
                    """
            params = (api_key, people_id, readonly, dba, expire_time)
        else:
            sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_QUEUED)
                    VALUES (%s,%s,%s,%s,'0','0')
                    """
            params = (api_key, people_id, readonly, dba,)

        return apis["NODES"].new_call(sql, params, meta)

    @haxdb.app.route("/NODES/save", methods=["GET", "POST"])
    @haxdb.app.route("/NODES/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        key_id = haxdb.data.session.get("nodes_id")

        meta = {}
        meta["api"] = "NODES"
        meta["action"] = "save"
        meta["col"] = col
        meta["rowid"] = rowid
        meta["val"] = val
        meta["oid"] = "NODES-%s-%s" % (rowid, col,)

        if int(key_id) == int(rowid):
            return haxdb.data.output(success=0, message="CANNOT UPDATE KEY YOU ARE CURRENTLY USING", meta=meta)

        sql = "UPDATE NODES SET {}=%s WHERE NODES_ID=%s"
        params = (val, rowid)
        return apis["NODES"].save_call(sql, params, meta, col, val, rowid)

    @haxdb.app.route("/NODES/delete", methods=["GET", "POST"])
    @haxdb.app.route("/NODES/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        key_id = haxdb.session.get("nodes_id")

        meta = {}
        meta["api"] = "NODES"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        if int(key_id) == int(rowid):
            return haxdb.data.output(success=0, message="CANNOT DELETE KEY YOU ARE CURRENTLY USING", meta=meta)

        sql = "DELETE FROM NODES WHERE NODES_ID=%s"
        params = (rowid,)

        return apis["NODES"].delete_call(sql, params, meta)
