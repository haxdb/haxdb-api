from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, api, mod_config, mod_def):
    global haxdb, db, config, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    for api_name in mod_def.keys():
        apis[api_name] = api.api_call(mod_def[api_name])


def run():
    @haxdb.app.route("/PEOPLE/list", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_list(category=None):
        def calc_row(row):
            row["ROW_NAME"] = "{} {}".format(row["PEOPLE_NAME_FIRST"],
                                             row["PEOPLE_NAME_LAST"])
            row["ROW_ID"] = row["PEOPLE_ID"]
            return row
        return apis["PEOPLE"].list_call(calc_row_function=calc_row)

    @haxdb.app.route("/PEOPLE/view", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_view(rowid=None):
        def c_row(row):
            row["ROW_NAME"] = "{} {}".format(row["PEOPLE_NAME_FIRST"],
                                             row["PEOPLE_NAME_LAST"])
            row["ROW_ID"] = row["PEOPLE_ID"]
            return row
        return apis["PEOPLE"].view_call(rowid=rowid, calc_row_function=c_row)

    @haxdb.app.route("/PEOPLE/csv", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_csv():
        return apis["PEOPLE"].list_call(output_format="CSV")

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
        return apis["PEOPLE"].new_call()

    @haxdb.app.route("/PEOPLE/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE/delete", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_delete(rowid=None):
        return apis["PEOPLE"].delete_call(rowid=rowid)

    @haxdb.app.route("/PEOPLE/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_upload():
        return apis["PEOPLE"].upload_call()

    @haxdb.app.route("/PEOPLE/download", methods=["GET", "POST"])
    @haxdb.app.route("/PEOPLE/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_download():
        return apis["PEOPLE"].download_call()

    @haxdb.app.route("/PEOPLE/thumbnail", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_thumbnail():
        return apis["PEOPLE"].thumbnail_call()
