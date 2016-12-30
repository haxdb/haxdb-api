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
    @haxdb.app.route("/ASSETS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/list/<path:query>", methods=["POST", "GET"])
    def mod_assets_list(query=None):
        meta = {}
        meta["api"] = "ASSETS"
        meta["action"] = "list"

        sql = """
        SELECT *
        FROM ASSETS
        """
        params = ()
        return apis["ASSETS"].list_call(sql, params, meta)

    @haxdb.app.route("/ASSETS/view", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/view/<int:rowid>", methods=["POST", "GET"])
    def mod_assets_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "ASSETS"
        meta["action"] = "view"
        meta["rowid"] = rowid

        sql = """
        SELECT *
        FROM ASSETS
        WHERE ASSETS_ID=%s
        """
        params = (rowid,)
        return apis["ASSETS"].view_call(sql, params, meta)

    @haxdb.app.route("/ASSETS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_new(name=None):
        name = name or haxdb.data.var.get("name")

        meta = {}
        meta["api"] = "ASSETS"
        meta["action"] = "new"
        meta["name"] = name

        sql = "INSERT INTO ASSETS (ASSETS_NAME, ASSETS_QUANTITY, ASSETS_INTERNAL) VALUES (%s, 1, 0)"
        params = (name, )

        return apis["ASSETS"].new_call(sql, params, meta)

    @haxdb.app.route("/ASSETS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSETS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "ASSETS"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM ASSETS WHERE ASSETS_ID=%s and ASSETS_INTERNAL!=1"
        params = (rowid,)

        return apis["ASSETS"].delete_call(sql, params, meta)

    @haxdb.app.route("/ASSETS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSETS/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")

        meta = {}
        meta["api"] = "ASSETS"
        meta["action"] = "save"
        meta["column"] = col
        meta["rowid"] = rowid
        meta["val"] = val
        meta["oid"] = "ASSETS-%s-%s" % (rowid, col,)

        sql = "UPDATE ASSETS SET {}=%s WHERE ASSETS_ID=%s and ASSETS_INTERNAL!=1"
        params = (val, rowid,)
        return apis["ASSETS"].save_call(sql, params, meta, col, val, rowid)

    @haxdb.app.route("/ASSET_LINKS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/list/<int:assets_id>", methods=["POST", "GET"])
    def mod_asset_links_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")

        meta = {}
        meta["api"] = "ASSET_LINKS"
        meta["action"] = "list"
        meta["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=%s"
        db.query(sql, (assets_id,))
        row = db.next()
        meta["assets_name"] = row["ASSETS_NAME"]

        sql = """
        SELECT ASSET_LINKS.*
        FROM ASSETS
        JOIN ASSET_LINKS ON ASSET_LINKS_ASSETS_ID=ASSETS_ID AND ASSETS_ID=%s
        """
        params = (assets_id,)

        return apis["ASSET_LINKS"].list_call(sql, params, meta)

    @haxdb.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>/<link>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_new(assets_id=None, name=None, link=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        name = name or haxdb.data.var.get("name")

        meta = {}
        meta["api"] = "ASSET_LINKS"
        meta["action"] = "new"
        meta["assets_id"] = assets_id
        meta["name"] = name

        sql = "INSERT INTO ASSET_LINKS (ASSET_LINKS_ASSETS_ID, ASSET_LINKS_NAME, ASSET_LINKS_ORDER) "
        sql += "VALUES (%s, %s, 999)"
        params = (assets_id, name,)
        return apis["ASSET_LINKS"].new_call(sql, params, meta)

    @haxdb.app.route("/ASSET_LINKS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_LINKS/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")

        meta = {}
        meta["api"] = "ASSET_LINKS"
        meta["action"] = "save"
        meta["rowid"] = rowid
        meta["col"] = col
        meta["val"] = val
        meta["oid"] = "ASSET_LINKS-%s-%s" % (rowid, col,)

        sql = "UPDATE ASSET_LINKS SET {}=%s WHERE ASSET_LINKS_ID=%s"
        params = (val, rowid,)
        return apis["ASSET_LINKS"].save_call(sql, params, meta, col, val, rowid)

    @haxdb.app.route("/ASSET_LINKS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_LINKS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "ASSET_LINKS"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM ASSET_LINKS WHERE ASSET_LINKS_ID=%s"
        params = (rowid,)
        return apis["ASSET_LINKS"].delete_call(sql, params, meta)

    @haxdb.app.route("/ASSET_AUTHS/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/list/<int:assets_id>", methods=["POST", "GET"])
    def mod_ASSET_AUTHS_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")

        meta = {}
        meta["api"] = "ASSET_AUTHS"
        meta["action"] = "list"
        meta["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=%s"
        db.query(sql, (assets_id,))
        row = db.next()
        meta["assets_name"] = row["ASSETS_NAME"]

        sql = """
        SELECT
        ASSET_AUTHS.*,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST, PEOPLE_EMAIL
        FROM ASSET_AUTHS
        JOIN PEOPLE ON ASSET_AUTHS_PEOPLE_ID = PEOPLE_ID and ASSET_AUTHS_ASSETS_ID=%s
        """
        params = (assets_id,)
        return apis["ASSET_AUTHS"].list_call(sql, params, meta)

    @haxdb.app.route("/ASSET_AUTHS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/new/<int:assets_id>/<int:people_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_new(assets_id=None, people_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        people_id = people_id or haxdb.data.var.get("people_id")

        meta = {}
        meta["api"] = "ASSET_AUTHS"
        meta["action"] = "new"
        meta["assets_id"] = assets_id
        meta["people_id"] = people_id

        sql = "INSERT INTO ASSET_AUTHS (ASSET_AUTHS_ASSETS_ID, ASSET_AUTHS_PEOPLE_ID) "
        sql += "VALUES (%s, %s)"
        params = (assets_id, people_id,)
        return apis["ASSET_AUTHS"].new_call(sql, params, meta)

    @haxdb.app.route("/ASSET_AUTHS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:assets_id>/<int:people_id>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_delete(rowid=None, assets_id=None, people_id=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        people_id = people_id or haxdb.data.var.get("people_id")

        meta = {}
        meta["api"] = "ASSET_AUTHS"
        meta["action"] = "delete"
        meta["rowid"] = rowid
        meta["assets_id"] = assets_id
        meta["people_id"] = people_id

        if rowid:
            sql = "DELETE FROM ASSET_AUTHS WHERE ASSET_AUTHS_ID=%s"
            params = (rowid,)

        elif assets_id and people_id:
            sql = "DELETE FROM ASSET_AUTH WHERE ASSET_AUTHS_ASSETS_ID=%s and ASSET_AUTHS_PEOPLE_ID=%s"
            params = (assets_id, people_id,)

        else:
            return haxdb.data.output(success=0, message="MISSING VALUES: rowid (or assets_id and people_id)", meta=meta)

        return apis["ASSET_AUTHS"].delete_call(sql, params, meta)
