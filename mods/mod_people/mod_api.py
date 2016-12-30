from flask import request, send_from_directory
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
    @haxdb.app.route("/PEOPLE/list", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_list(category=None):
        return apis["PEOPLE"].list_call()

    @haxdb.app.route("/PEOPLE/view", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_view(rowid=None):
        return apis["PEOPLE"].view_call(rowid=rowid)

    @haxdb.app.route("/PEOPLE/save", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_save(rowid=None):
        return apis["PEOPLE"].save_call(rowid=rowid)

    @haxdb.app.route("/PEOPLE/new", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_new():
        return apis["PEOPLE"].new_call(sql, params, meta)

    @haxdb.app.route("/PEOPLE/delete/", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_delete(rowid=None):
        return apis["PEOPLE"].delete_call(rowid=rowid)
