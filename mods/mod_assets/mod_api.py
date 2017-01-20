import mod_data
from flask import request
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
apis = {}


def get_assets_name(rowid):
        sql = """
        SELECT ASSETS_NAME FROM ASSETS WHERE ASSETS_ID=%s
        """
        row = db.qaf(sql, (rowid,))
        if not row:
            return None
        return row["ASSETS_NAME"]


def init(app_haxdb, mod_config, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def run():
    @haxdb.app.route("/ASSETS/list", methods=["POST", "GET"])
    def mod_assets_list():
        return apis["ASSETS"].list_call()

    @haxdb.app.route("/ASSETS/view", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/view/<int:rowid>", methods=["POST", "GET"])
    def mod_assets_view(rowid=None):
        return apis["ASSETS"].view_call(rowid=rowid)

    @haxdb.app.route("/ASSETS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_new(name=None):
        return apis["ASSETS"].new_call()

    @haxdb.app.route("/ASSETS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSETS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_delete(rowid=None):
        return apis["ASSETS"].delete_call(rowid=rowid)

    @haxdb.app.route("/ASSETS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSETS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_save(rowid=None):
        return apis["ASSETS"].save_call(rowid=rowid)

    @haxdb.app.route("/ASSET_LINKS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/list/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_asset_links_asset(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")

        meta = {"name": get_assets_name(ASSETS_ID)}

        t = """
        (
        select A.*, B.ASSETS_NAME
        FROM ASSET_LINKS A
        JOIN ASSETS B ON ASSETS_ID=ASSET_LINKS_ASSETS_ID
        WHERE
        ASSET_LINKS_ASSETS_ID=%s
        )
        """
        params = (ASSETS_ID,)

        return apis["ASSET_LINKS"].list_call(table=t, params=params, meta=meta)

    @haxdb.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:ASSETS_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_new(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")
        defaults = {
            "ASSET_LINKS_ASSETS_ID": ASSETS_ID,
        }
        return apis["ASSET_LINKS"].new_call(defaults=defaults)

    @haxdb.app.route("/ASSET_LINKS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_LINKS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_save(rowid=None):
        return apis["ASSET_LINKS"].save_call(rowid=rowid)

    @haxdb.app.route("/ASSET_LINKS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_LINKS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_delete(rowid=None):
        return apis["ASSET_LINKS"].delete_call(rowid=rowid)

    @haxdb.app.route("/ASSET_AUTHS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/list/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_ASSET_AUTHS_asset(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")

        meta = {"name": get_assets_name(ASSETS_ID)}

        t = """
        (
        select A.*,
        B.ASSETS_NAME,
        C.PEOPLE_NAME_FIRST, C.PEOPLE_NAME_LAST, C.PEOPLE_EMAIL
        FROM ASSET_AUTHS A
        JOIN ASSETS B ON ASSETS_ID=ASSET_AUTHS_ASSETS_ID
        JOIN PEOPLE C ON ASSET_AUTHS_PEOPLE_ID=PEOPLE_ID
        WHERE
        ASSET_AUTHS_ASSETS_ID=%s
        )
        """
        params = (ASSETS_ID,)

        return apis["ASSET_AUTHS"].list_call(table=t, params=params, meta=meta)

    @haxdb.app.route("/ASSET_AUTHS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/new/<int:ASSETS_ID>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_new(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")
        defaults = {
            "ASSET_AUTHS_ASSETS_ID": ASSETS_ID,
            "ASSET_AUTHS_ENABLED": 1,
        }
        return apis["ASSET_AUTHS"].new_call(defaults=defaults)

    @haxdb.app.route("/ASSET_AUTHS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_delete(rowid=None):
        return apis["ASSET_AUTHS"].delete_call(rowid=rowid)

    @haxdb.app.route("/ASSET_AUTHS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_auths_save(rowid=None):
        return apis["ASSET_AUTHS"].save_call(rowid=rowid)
