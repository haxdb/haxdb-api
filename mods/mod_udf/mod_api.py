from flask import request
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def run():
    @haxdb.app.route("/UDF/list", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/list/<UDF_CONTEXT>", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/list/<UDF_CONTEXT>/<int:UDF_CONTEXT_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_list(UDF_CONTEXT=None, UDF_CONTEXT_ID=None):
        UDF_CONTEXT = UDF_CONTEXT or haxdb.data.var.get("UDF_CONTEXT")
        UDF_CONTEXT_ID = UDF_CONTEXT_ID or haxdb.data.var.get("UDF_CONTEXT_ID") or 0
        disabled = haxdb.data.var.get("disabled")
        meta = {"name": UDF_CONTEXT}

        t = """
        (
            SELECT *,
            UDF_ID AS ROW_ID, UDF_NAME AS ROW_NAME
            FROM UDF
            WHERE
            UDF_CONTEXT=%s
            AND UDF_CONTEXT_ID=%s
        )
        """
        p = (UDF_CONTEXT, UDF_CONTEXT_ID)
        if disabled == 1:
            t += " AND UDF_ENABLED=1 "

        return apis["UDF"].list_call(table=t, params=p, meta=meta)

    @haxdb.app.route("/UDF/new", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/new/<UDF_CONTEXT>", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/new/<UDF_CONTEXT>/<int:UDF_CONTEXT_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_new(UDF_CONTEXT=None, UDF_CONTEXT_ID=None):
        UDF_CONTEXT = UDF_CONTEXT or haxdb.data.var.get("UDF_CONTEXT")
        UDF_CONTEXT_ID = UDF_CONTEXT_ID or haxdb.data.var.get("UDF_CONTEXT_ID") or 0

        defaults = {
            "UDF_CONTEXT": UDF_CONTEXT,
            "UDF_CONTEXT_ID": UDF_CONTEXT_ID,
        }
        return apis["UDF"].new_call(defaults=defaults)

    @haxdb.app.route("/UDF/delete", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_delete(rowid=None):
        return apis["UDF"].delete_call(rowid=rowid)

    @haxdb.app.route("/UDF/save", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_save(rowid=None, col=None, val=None):
        return apis["UDF"].save_call(rowid=rowid)
