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
        lists_name = lists_name or haxdb.data.var.get("lists_name")
        include_disabled = haxdb.data.var.get("include_disabled")

        if not context_id and not lists_id and not lists_name:
            return haxdb.data.output(success=0, meta=meta, message="MISSING VALUE: lists_id or lists_name")

        meta = {}
        meta["context_name"] = lists_name
        if lists_id:
            row = db.qaf("SELECT * FROM LISTS WHERE LISTS_ID=%s", (lists_id,))
            meta["context_name"] = row["LISTS_NAME"]

        sql = """
            SELECT
            *
            FROM LIST_ITEMS
            JOIN LISTS ON LIST_ITEMS_LISTS_ID=LISTS_ID
        """
        params = ()
        if lists_id:
            sql += " AND LISTS_ID=%s"
            params += (lists_id,)
        elif lists_name:
            sql += " AND LISTS_NAME=%s"
            params += (lists_name,)

        apis["LIST_ITEMS"].context_id(context_id)
        return apis["LIST_ITEMS"].list_call(sql=sql, params=params, meta=meta)

    @haxdb.app.route("/LIST_ITEMS/new", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:context_id>", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:context_id>/<value>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_new(context_id=None, value=None):
        context_id = context_id or haxdb.data.var.get("context_id")
        value = value or haxdb.data.var.get("value")

        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "new"
        meta["context_id"] = context_id
        meta["value"] = value

        sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) "
        sql += "VALUES (%s, %s, %s, 0, 999)"
        params = (context_id, value, value,)
        return apis["LIST_ITEMS"].new_call(sql, params, meta)

    @haxdb.app.route("/LIST_ITEMS/save", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        context_id = haxdb.data.var.get("context_id") or None

        if not context_id and rowid:
            row = db.qaf("SELECT * FROM LIST_ITEMS WHERE LIST_ITEMS_ID=%s", (rowid,))
            context_id = row["LIST_ITEMS_LISTS_ID"]

        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "save"
        meta["col"] = col
        meta["rowid"] = rowid
        meta["val"] = val
        meta["oid"] = "LIST_ITEMS-%s-%s" % (rowid, col)

        sql = "UPDATE LIST_ITEMS SET {}=%s WHERE LIST_ITEMS_ID=%s"
        params = (val, rowid,)
        apis["LIST_ITEMS"].udf_context_id = context_id
        return apis["LIST_ITEMS"].save_call(sql, params, meta, col, val, rowid=rowid)

    @haxdb.app.route("/LIST_ITEMS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM LIST_ITEMS WHERE LIST_ITEMS_ID=%s"
        params = (rowid,)
        return apis["LIST_ITEMS"].delete_call(sql, params, meta)
