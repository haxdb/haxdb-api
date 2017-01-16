import mod_data
from flask import request
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, mod_def):
    global haxdb, db, config, tools
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def run():
    @haxdb.app.route("/LISTS/list", methods=["POST", "GET"])
    @haxdb.require_auth
    def mod_lists_list():
        return apis["LISTS"].list_call()

    @haxdb.app.route("/LISTS/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_new(name=None):
        return apis["LISTS"].new_call()

    @haxdb.app.route("/LISTS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/LISTS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_delete(rowid=None):
        return apis["LISTS"].delete_call(rowid=rowid)

    @haxdb.app.route("/LISTS/save", methods=["GET", "POST"])
    @haxdb.app.route("/LISTS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_save(rowid=None):
        return apis["LISTS"].save_call(rowid=rowid)

    @haxdb.app.route("/LIST_ITEMS/list", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/list/<int:context_id>", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/list/<lists_name>", methods=["POST", "GET"])
    @haxdb.require_auth
    def mod_list_items_list(context_id=None, lists_name=None):
        context_id = context_id or haxdb.data.var.get("context_id") or haxdb.data.var.get("lists_id")
        page_name = lists_name or haxdb.data.var.get("page_name") or haxdb.data.var.get("lists_name")
        include_disabled = haxdb.data.var.get("include_disabled")

        if not context_id and not page_name:
            meta = apis["LIST_ITEMS"].get_meta("list")
            return haxdb.data.output(success=0, meta=meta, message="MISSING VALUE: context_id or page_name")

        if page_name and not context_id:
            row = haxdb.db.qaf("select LISTS_ID from LISTS where LISTS_NAME=%s", (page_name,))
            try:
                context_id = row["LISTS_ID"]
            except:
                meta = apis["LIST_ITEMS"].get_meta("list")
                return haxdb.data.output(success=0, meta=meta, message="UNKNOWN LIST")

        if not page_name:
            row = haxdb.db.qaf("select LISTS_NAME from LISTS where LISTS_ID=%s", (context_id,))
            try:
                page_name = row["LISTS_NAME"]
            except:
                meta = apis["LIST_ITEMS"].get_meta("list")
                return haxdb.data.output(success=0, meta=meta, message="UNKNOWN LIST")

        meta = {}
        meta["page_name"] = page_name

        sql = """
            SELECT L.*, UDF_NAME, UDF_DATA_VALUE
            FROM
            (
            SELECT
            *
            FROM LIST_ITEMS
            JOIN LISTS ON LIST_ITEMS_LISTS_ID=LISTS_ID AND LISTS_ID=%s
            ) L
        """
        params = (context_id, )

        apis["LIST_ITEMS"].context_id(context_id)
        return apis["LIST_ITEMS"].list_call(sql=sql, params=params, meta=meta)

    @haxdb.app.route("/LIST_ITEMS/new", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_new(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id")
        apis["LIST_ITEMS"].context_id(context_id)
        return apis["LIST_ITEMS"].new_call()


    @haxdb.app.route("/LIST_ITEMS/save", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_save(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["LIST_ITEMS"].save_call(rowid=rowid)

    @haxdb.app.route("/LIST_ITEMS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["LIST_ITEMS"].delete_call(rowid=rowid)
