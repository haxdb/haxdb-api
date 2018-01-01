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
methods = ["POST", "GET"]


def init(app_haxdb, api, mod_config, mod_def):
    global haxdb, db, config
    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    for api_name in mod_def.keys():
        apis[api_name] = api.api_call(mod_def[api_name])


def run():
    global haxdb, db, config

    @haxdb.app.before_request
    def mod_api_keys_before_request():
        session.permanent = True
        key = haxdb.get("api_key", use_session=True)

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
                haxdb.session("api_authenticated", 1)
                haxdb.session("api_people_id", row["NODES_PEOPLE_ID"])
                haxdb.session("nodes_id", row["NODES_ID"])
                haxdb.session("nodes_name", row["NODES_NAME"])
                haxdb.session("api_key", row["NODES_API_KEY"])
                haxdb.session("api_dba", row["NODES_DBA"])
            else:
                haxdb.session("api_authenticated", 0)

    @haxdb.route("/NODES/list", methods=haxdb.METHOD)
    def NODES_list():
        return haxdb.api.list_call(mod_def["NODES"])

    @haxdb.route("/NODES/view", methods=haxdb.METHOD)
    def NODES_view():
        return haxdb.api.view_call(mod_def["NODES"])

    @haxdb.route("/NODES/new", methods=haxdb.METHOD)
    def NODES_new():
        vals = {
            'api_key': haxdb.func("APIKEY_CREATE")(),
        }
        
        return haxdb.api.new_call(mod_def["NODES"], values=vals)

    @haxdb.route("/NODES/delete", methods=haxdb.METHOD)
    def NODES_delete():
        return haxdb.api.delete_call(mod_def["NODES"])

    @haxdb.route("/NODES/save", methods=haxdb.METHOD)
    def NODES_save():
        return haxdb.api.save_call(mod_def["NODES"])
