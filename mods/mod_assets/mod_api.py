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
    @haxdb.app.route("/ASSET_LINKS/list/<int:context_id>", methods=["POST", "GET"])
    def mod_asset_links_asset(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id")
        apis["ASSET_LINKS"].context_id(context_id)
        return apis["ASSET_LINKS"].list_call()

    @haxdb.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_new(context_id):
        context_id = context_id or haxdb.data.var.get("context_id")
        apis["ASSET_LINKS"].context_id(context_id)
        return apis["ASSET_LINKS"].new_call()

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
    @haxdb.app.route("/ASSET_AUTHS/list/<int:context_id>", methods=["POST", "GET"])
    def mod_ASSET_AUTHS_asset(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id")
        apis["ASSET_AUTHS"].context_id(context_id)
        return apis["ASSET_AUTHS"].list_call()

    @haxdb.app.route("/ASSET_AUTHS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/new/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_new(context_id=None):
        context_id = context_id or haxdb.data.var.get("context_id")
        apis["ASSET_AUTHS"].context_id(context_id)
        return apis["ASSET_AUTHS"].new_call()

    @haxdb.app.route("/ASSET_AUTHS/delete", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["ASSET_AUTHS"].delete_call(rowid=rowid)

    @haxdb.app.route("/ASSET_AUTHS/save", methods=["GET", "POST"])
    @haxdb.app.route("/ASSET_AUTHS/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_auths_save(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["ASSET_AUTHS"].save_call(rowid=rowid)
