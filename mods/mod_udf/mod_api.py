import mod_data
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
    @haxdb.app.route("/UDF/list/<context>", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/list/<context>/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_list(context=None, context_id=None):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0

        try:
            disabled = int(haxdb.data.var.get("disabled"))
        except:
            disabled = 0

        if disabled == 1:
            sql = """
            SELECT *
            FROM ( SELECT * FROM UDF U2 WHERE U2.UDF_CONTEXT=%s AND U2.UDF_CONTEXT_ID=%s) UDF2
            """
        else:
            sql = """
            SELECT *
            FROM ( SELECT * FROM UDF U2 WHERE U2.UDF_CONTEXT=%s AND U2.UDF_CONTEXT_ID=%s AND U2.UDF_ENABLED=1 ) UDF2
            """
        params = (context, context_id,)

        meta = apis["UDF"].get_meta("list")
        meta["page_name"] = context
        return apis["UDF"].list_call(sql=sql, params=params, meta=meta)

    @haxdb.app.route("/UDF/new", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_new(name=None):
        name = name or haxdb.data.var.get("name")
        context = haxdb.data.var.get("context")
        context_id = haxdb.data.var.get("context_id") or 0

        defaults = {
            "UDF_CONTEXT": context,
            "UDF_CONTEXT_ID": context_id,
        }
        return apis["UDF"].new_call(defaults=defaults)

    @haxdb.app.route("/UDF/delete", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["UDF"].delete_call(rowid=rowid)

    @haxdb.app.route("/UDF/save", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["UDF"].save_call(rowid=rowid)
