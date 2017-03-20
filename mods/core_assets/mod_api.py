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
        def calc_row(row):
            row["ROW_NAME"] = row["ASSETS_NAME"]
            row["ROW_ID"] = row["ASSETS_ID"]
            return row
        return apis["ASSETS"].list_call(calc_row_function=calc_row)

    @haxdb.app.route("/ASSETS/csv", methods=["POST", "GET"])
    def mod_assets_csv():
        return apis["ASSETS"].list_call(output_format="CSV")

    @haxdb.app.route("/ASSETS/view", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/view/<int:rowid>", methods=["POST", "GET"])
    def mod_assets_view(rowid=None):
        def calc_row(row):
            row["ROW_NAME"] = row["ASSETS_NAME"]
            row["ROW_ID"] = row["ASSETS_ID"]
            return row
        return apis["ASSETS"].view_call(rowid=rowid,  calc_row_function=calc_row)

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

    @haxdb.app.route("/ASSETS/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSETS_upload():
        return apis["ASSETS"].upload_call()

    @haxdb.app.route("/ASSETS/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_download(rowid=None):
        return apis["ASSETS"].download_call()

    @haxdb.app.route("/ASSET_LINKS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/list/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_asset_links_list(ASSETS_ID=None):
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

    @haxdb.app.route("/ASSET_LINKS/csv", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/csv/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_asset_links_csv(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")

        t = """
        (
        select A.*, B.ASSETS_NAME
        FROM ASSET_LINKS A
        JOIN ASSETS B ON ASSETS_ID=ASSET_LINKS_ASSETS_ID
        WHERE
        ASSET_LINKS_ASSETS_ID=%s
        )
        """
        p = (ASSETS_ID,)

        return apis["ASSET_LINKS"].list_call(table=t, params=p,
                                             output_format="CSV")

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

    @haxdb.app.route("/ASSET_LINKS/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_LINKS_upload():
        return apis["ASSET_LINKS"].upload_call()

    @haxdb.app.route("/ASSET_LINKS/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_LINKS_download(rowid=None):
        return apis["ASSET_LINKS"].download_call()

    @haxdb.app.route("/ASSET_AUTHS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/list/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_ASSET_AUTHS_list(ASSETS_ID=None):
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

    @haxdb.app.route("/ASSET_AUTHS/csv", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/csv/<int:ASSETS_ID>", methods=["POST", "GET"])
    def mod_ASSET_AUTHS_csv(ASSETS_ID=None):
        ASSETS_ID = ASSETS_ID or haxdb.data.var.get("ASSETS_ID")

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
        p = (ASSETS_ID,)

        return apis["ASSET_AUTHS"].list_call(table=t, params=p,
                                             output_format="CSV")

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

    @haxdb.app.route("/ASSET_AUTHS/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_upload():
        return apis["ASSET_AUTHS"].upload_call()

    @haxdb.app.route("/ASSET_AUTHS/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_download(rowid=None):
        return apis["ASSET_AUTHS"].download_call()
