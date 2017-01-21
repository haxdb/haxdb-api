from flask import request
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
apis = {}


def get_lists_name(rowid):
        sql = """
        SELECT LISTS_NAME FROM LISTS WHERE LISTS_ID=%s
        """
        row = db.qaf(sql, (rowid,))
        if not row:
            return None
        return row["LISTS_NAME"]


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
    @haxdb.app.route("/LIST_ITEMS/list/<int:LISTS_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    def mod_list_items_list(LISTS_ID=None):
        LISTS_ID = LISTS_ID or haxdb.data.var.get("LISTS_ID")

        meta = {"name": get_lists_name(LISTS_ID)}

        t = """
        (
        select A.*, B.LISTS_NAME
        FROM LIST_ITEMS A
        JOIN LISTS B ON LISTS_ID=LIST_ITEMS_LISTS_ID
        WHERE
        LIST_ITEMS_LISTS_ID=%s
        )
        """
        params = (LISTS_ID,)

        return apis["LIST_ITEMS"].list_call(table=t, params=params, meta=meta)

    @haxdb.app.route("/LIST_ITEMS/new", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:LISTS_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_new(LISTS_ID=None):
        LISTS_ID = LISTS_ID or haxdb.data.var.get("LISTS_ID")
        defaults = {
            "LIST_ITEMS_LISTS_ID": LISTS_ID,
            "LIST_ITEMS_ENABLED": 1,
        }
        return apis["LIST_ITEMS"].new_call(defaults=defaults)


    @haxdb.app.route("/LIST_ITEMS/save", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_save(rowid=None):
        return apis["LIST_ITEMS"].save_call(rowid=rowid)

    @haxdb.app.route("/LIST_ITEMS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/LIST_ITEMS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_delete(rowid=None):
        return apis["LIST_ITEMS"].delete_call(rowid=rowid)
