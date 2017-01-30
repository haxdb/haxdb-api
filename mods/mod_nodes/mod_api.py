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
    def mod_NODES_list():
        sql = "DELETE FROM NODES WHERE NODES_EXPIRE<%s"
        db.query(sql, (time.time(),))
        db.commit()

        table = """
        (
        SELECT
        NODES.*,
        NODES.NODES_ID AS ROW_ID, NODES.NODES_NAME AS ROW_NAME,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST,
        ASSETS_NAME
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        )
        """

        return apis["NODES"].list_call(table=table)

    @haxdb.app.route("/NODES/csv", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_NODES_csv():
        table = """
        (
        SELECT
        NODES.*,
        NODES.NODES_ID AS ROW_ID, NODES.NODES_NAME AS ROW_NAME,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST,
        ASSETS_NAME
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        )
        """

        return apis["NODES"].list_call(table=table, output_format="CSV")

    @haxdb.app.route("/NODES/view", methods=["POST", "GET"])
    @haxdb.app.route("/NODES/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_NODES_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        table = """
        (
        SELECT
        NODES.*,
        NODES.NODES_ID AS ROW_ID, NODES.NODES_NAME AS ROW_NAME,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST,
        ASSETS_NAME
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        )
        """
        return apis["NODES"].view_call(table=table, rowid=rowid)

    @haxdb.app.route("/NODES/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_create():
        expire = haxdb.data.var.get("expire")

        defaults = {
            "NODES_API_KEY": base64.urlsafe_b64encode(os.urandom(500))[5:260]
        }

        if expire:
            try:
                defaults["NODES_EXPIRE"] = int(time.time()) + int(expire)
            except:
                message = "expire should be a valid integer (seconds)"
                meta = apis["NODES"].get_meta("new")
                return haxdb.data.output(success=0, meta=meta, message=message)

        return apis["NODES"].new_call(defaults=defaults)

    @haxdb.app.route("/NODES/save", methods=["GET", "POST"])
    @haxdb.app.route("/NODES/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_save(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        key_id = haxdb.session.get("nodes_id")

        if int(key_id) == int(rowid):
            message = "CANNOT UPDATE KEY YOU ARE CURRENTLY USING"
            meta = apis["NODES"].get_meta("save")
            return haxdb.data.output(success=0, meta=meta, message=message)
        return apis["NODES"].save_call(rowid=rowid)

    @haxdb.app.route("/NODES/delete", methods=["GET", "POST"])
    @haxdb.app.route("/NODES/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        key_id = haxdb.session.get("nodes_id")

        if int(key_id) == int(rowid):
            message = "CANNOT DELETE KEY YOU ARE CURRENTLY USING"
            meta = apis["NODES"].get_meta("delete")
            return haxdb.data.output(success=0, meta=meta, message=message)

        return apis["NODES"].delete_call(rowid=rowid)
