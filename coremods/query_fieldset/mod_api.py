from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os
import shlex

haxdb = None
db = None
config = None
apis = {}


def get_fieldset_cols(rowid=None):
    if rowid:
        sql = """
            SELECT * FROM FIELDSET_COLS
            WHERE FIELDSET_ID=%s
        """
        row = db.qaf(sql, (rowid,))
    else:
        sql = """
            SELECT * FROM FIELDSET_COLS
        """
        row = db.qaf(sql)

    FIELDSET_COLS = {}
    while row:
        fid = row["FIELDSET_COLS_FIELDSET_ID"]
        if fid not in FIELDSET_COLS:
            FIELDSET_COLS[fid] = []
        FIELDSET_COLS[fid].append(row["FIELDSET_COLS_COL"])
        row = db.next()
    return FIELDSET_COLS


def init(app_haxdb, api, mod_config, mod_def):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = mod_config

    for api_name in mod_def.keys():
        apis[api_name] = api.api_call(mod_def[api_name])


def run():
    @haxdb.route("/FIELDSET/list", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_FIELDSET_list():
        FIELDSET_COLS = get_fieldset_cols()

        def calc_row(row):
            try:
                row["COLS"] = FIELDSET_COLS[row["FIELDSET_ID"]]
            except:
                row["COLS"] = []
            row["ROW_ID"] = row["FIELDSET_ID"]
            row["ROW_NAME"] = row["FIELDSET_NAME"]
            return row

        FIELDSET_CONTEXT = haxdb.get("FIELDSET_CONTEXT")
        FIELDSET_CONTEXT_ID = haxdb.get("FIELDSET_CONTEXT_ID") or 0
        people_id = haxdb.session("api_people_id")

        m = {
            "FIELDSET_CONTEXT": FIELDSET_CONTEXT,
            "FIELDSET_CONTEXT_ID": FIELDSET_CONTEXT_ID,
        }

        t = """
        (
            SELECT * FROM FIELDSET
            WHERE FIELDSET_CONTEXT=%s and FIELDSET_CONTEXT_ID=%s AND
            FIELDSET_PEOPLE_ID IN (0,%s)
        )
        """
        p = (FIELDSET_CONTEXT, FIELDSET_CONTEXT_ID, people_id)
        return apis["FIELDSET"].list_call(table=t, params=p, meta=m, row_func=calc_row)

    @haxdb.route("/FIELDSET/view", methods=["POST", "GET"])
    @haxdb.route("/FIELDSET/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_FIELDSET_view(rowid=None):
        def c(row):
            try:
                row["COLS"] = get_fieldset_cols(row["FIELDSET_ID"])
            except:
                row["COLS"] = []
            row["ROW_ID"] = row["FIELDSET_ID"]
            row["ROW_NAME"] = row["FIELDSET_NAME"]
            return row

        return apis["FIELDSET"].view_call(rowid=rowid, row_func=c)

    @haxdb.route("/FIELDSET/save", methods=["GET", "POST"])
    @haxdb.route("/FIELDSET/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_save(rowid=None):
        rowid = rowid or haxdb.get("rowid")
        cols = haxdb.getlist("COLS")

        if cols:
            m = apis["FIELDSET"].get_meta("save")
            sql = """
            DELETE FROM FIELDSET_COLS WHERE FIELDSET_COLS_FIELDSET_ID=%s
            """
            db.query(sql, (rowid,))
            if db.error:
                return haxdb.output(success=0, meta=m, message=db.error)

            sql = """
            INSERT INTO FIELDSET_COLS
            (FIELDSET_COLS_FIELDSET_ID, FIELDSET_COLS_COL, FIELDSET_COLS_ORDER)
            VALUES (%s, %s, %s)
            """
            order = 0
            total = 0
            for col in cols:
                order += 1
                db.query(sql, (rowid, col, order))
                if db.error:
                    return haxdb.output(success=0, meta=m, message=db.error)
                total += db.rowcount
            m["rowcount"] = total
            db.commit()
            return apis["FIELDSET"].save_call(rowid=rowid, meta=m)

        else:
            return apis["FIELDSET"].save_call(rowid=rowid)

    @haxdb.route("/FIELDSET/new", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_new():
        FIELDSET_CONTEXT = haxdb.get("FIELDSET_CONTEXT")
        FIELDSET_CONTEXT_ID = haxdb.get("FIELDSET_CONTEXT_ID") or 0
        FIELDSET_NAME = haxdb.get("FIELDSET_NAME")
        user = haxdb.get("user") or 0
        cols = haxdb.getlist("COLS")
        people_id = 0

        try:
            if int(user) == 1:
                people_id = haxdb.session("api_people_id")
        except:
            pass

        m = apis["FIELDSET"].get_meta("new")

        sql = """
            INSERT INTO FIELDSET
            (FIELDSET_NAME, FIELDSET_CONTEXT,
            FIELDSET_CONTEXT_ID, FIELDSET_PEOPLE_ID)
            VALUES (%s, %s, %s, %s)
        """
        p = (FIELDSET_NAME, FIELDSET_CONTEXT, FIELDSET_CONTEXT_ID, people_id)
        db.query(sql, p)
        if db.error:
            return haxdb.output(success=0, message=db.error, meta=m)
        rowid = db.lastrowid
        m["rowid"] = rowid

        sql = """
        DELETE FROM FIELDSET_COLS WHERE FIELDSET_COLS_FIELDSET_ID=%s
        """
        db.query(sql, (rowid,))

        sql = """
        INSERT INTO FIELDSET_COLS
        (FIELDSET_COLS_FIELDSET_ID, FIELDSET_COLS_COL, FIELDSET_COLS_ORDER)
        VALUES (%s, %s, %s)
        """
        order = 0
        total = 0
        if cols:
            for col in cols:
                order += 1
                db.query(sql, (rowid, col, order))
                total += db.rowcount

        m["rowcount"] = total
        db.commit()
        return haxdb.output(success=1, meta=m, message="SAVED")

    @haxdb.route("/FIELDSET/delete", methods=["GET", "POST"])
    @haxdb.route("/FIELDSET/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_delete(rowid=None):
        return apis["FIELDSET"].delete_call(rowid=rowid)

    @haxdb.route("/FIELDSET/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_upload():
        return apis["FIELDSET"].upload_call()

    @haxdb.route("/FIELDSET/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_download(rowid=None):
        return apis["FIELDSET"].download_call()

    @haxdb.route("/QUERY/list", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_QUERY_list():
        QUERY_CONTEXT = haxdb.get("QUERY_CONTEXT")
        QUERY_CONTEXT_ID = haxdb.get("QUERY_CONTEXT_ID") or 0
        people_id = haxdb.session("api_people_id")

        m = {
            "QUERY_CONTEXT": QUERY_CONTEXT,
            "QUERY_CONTEXT_ID": QUERY_CONTEXT_ID,
        }

        t = """
        (
            SELECT *,
            QUERY_ID AS ROW_ID, QUERY_NAME AS ROW_NAME
            FROM QUERY
            WHERE QUERY_CONTEXT=%s and QUERY_CONTEXT_ID=%s AND
            QUERY_PEOPLE_ID IN (0,%s)
        )
        """
        p = (QUERY_CONTEXT, QUERY_CONTEXT_ID, people_id)
        return apis["QUERY"].list_call(table=t, params=p, meta=m)

    @haxdb.route("/QUERY/view", methods=["POST", "GET"])
    @haxdb.route("/QUERY/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_QUERY_view(rowid=None):
        def calc_row(row):
            row["ROW_NAME"] = row["QUERY_NAME"]
            row["ROW_ID"] = row["QUERY_ID"]
            return row
        return apis["QUERY"].view_call(rowid=rowid, row_func=calc_row)

    @haxdb.route("/QUERY/save", methods=["GET", "POST"])
    @haxdb.route("/QUERY/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_save(rowid=None):
        return apis["QUERY"].save_call(rowid=rowid)

    @haxdb.route("/QUERY/new", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_new():
        QUERY_CONTEXT = haxdb.get("QUERY_CONTEXT")
        QUERY_CONTEXT_ID = haxdb.get("QUERY_CONTEXT_ID") or 0
        user = haxdb.get("user") or 0

        people_id = 0
        if user == 1:
            people_id = haxdb.session("api_people_id")

        defaults = {
            "QUERY_CONTEXT": QUERY_CONTEXT,
            "QUERY_CONTEXT_ID": QUERY_CONTEXT_ID,
            "QUERY_PEOPLE_ID": people_id
        }
        return apis["QUERY"].new_call(defaults=defaults)

    @haxdb.route("/QUERY/delete", methods=["GET", "POST"])
    @haxdb.route("/QUERY/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_delete(rowid=None):
        return apis["QUERY"].delete_call(rowid=rowid)

    @haxdb.route("/QUERY/upload", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_upload():
        return apis["QUERY"].upload_call()

    @haxdb.route("/QUERY/download", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_download(rowid=None):
        return apis["QUERY"].download_call()
