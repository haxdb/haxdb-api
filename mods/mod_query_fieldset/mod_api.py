import mod_data
from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os
import shlex

haxdb = None
db = None
config = None
apis = {}


def init(app_haxdb, mod_def):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = haxdb.db
    config = haxdb.config

    for api_name in mod_def.keys():
        apis[api_name] = haxdb.api.api_call(mod_def[api_name])


def run():
    @haxdb.app.route("/FIELDSET/list", methods=["POST", "GET"])
    @haxdb.app.route("/FIELDSET/list/<context>", methods=["POST", "GET"])
    @haxdb.app.route("/FIELDSET/list/<context>/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_FIELDSET_list(context=None, context_id=0):
        def calc_row(row):
            try:
                row["COLS"] = FIELDSET_COLS[row["FIELDSET_ID"]]
            except:
                row["COLS"] = []
            return row

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

        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0
        people_id = haxdb.data.session.get("api_people_id")

        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "list"
        meta["context"] = context
        meta["context_id"] = context_id

        sql = """
        SELECT F.*, UDF_NAME, UDF_DATA_VALUE FROM
        (
        SELECT * FROM FIELDSET WHERE FIELDSET_CONTEXT=%s and FIELDSET_CONTEXT_ID=%s AND
        FIELDSET_PEOPLE_ID IN (0,%s)
        ) F
        """
        params = (context, context_id, people_id)
        return apis["FIELDSET"].list_call(sql=sql, params=params, meta=meta, calc_row_function=calc_row)

    @haxdb.app.route("/FIELDSET/view", methods=["POST", "GET"])
    @haxdb.app.route("/FIELDSET/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_FIELDSET_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "view"
        meta["rowid"] = rowid

        sql = """
        SELECT * FROM FIELDSET
        WHERE FIELDSET_ID=%s
        """
        params = (rowid,)
        return apis["FIELDSET"].view_call(sql, params, meta)

    @haxdb.app.route("/FIELDSET/save", methods=["GET", "POST"])
    @haxdb.app.route("/FIELDSET/save/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_save(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        cols = haxdb.data.var.getlist("COLS")

        if cols:
            meta = {}
            sql = """
            DELETE FROM FIELDSET_COLS WHERE FIELDSET_COLS_FIELDSET_ID=%s
            """
            db.query(sql, (rowid,))
            if db.error:
                return haxdb.data.output(success=0, meta=meta, message=db.error)

            sql = """
            INSERT INTO FIELDSET_COLS(FIELDSET_COLS_FIELDSET_ID, FIELDSET_COLS_COL, FIELDSET_COLS_ORDER)
            VALUES (%s, %s, %s)
            """
            order = 0
            total = 0
            for col in cols:
                order += 1
                db.query(sql, (rowid, col, order))
                if db.error:
                    return haxdb.data.output(success=0, meta=meta, message=db.error)

                total += db.rowcount
            meta["rowcount"] = total
            db.commit()
            return apis["FIELDSET"].save_call(rowid=rowid, meta=meta)

        else:
            return apis["FIELDSET"].save_call(rowid=rowid)

    @haxdb.app.route("/FIELDSET/new", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_new():
        context = haxdb.data.var.get("context")
        context_id = haxdb.data.var.get("context_id") or 0
        name = haxdb.data.var.get("FIELDSET_NAME")
        global_fieldset = haxdb.data.var.get("global") or 0
        cols = haxdb.data.var.getlist("COLS")

        people_id = 0
        try:
            if int(global_fieldset) != 1:
                people_id = haxdb.data.session.get("api_people_id")
        except:
            pass

        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "new"

        if not name:
            return haxdb.data.output(success=0, message="MISSING INPUT: FIELDSET_NAME", meta=meta)

        sql = "INSERT INTO FIELDSET (FIELDSET_NAME, FIELDSET_CONTEXT, FIELDSET_CONTEXT_ID, FIELDSET_PEOPLE_ID) VALUES (%s, %s, %s, %s)"
        params = (name, context, context_id, people_id)
        db.query(sql, params)
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        rowid = db.lastrowid
        meta["rowid"] = rowid

        sql = """
        DELETE FROM FIELDSET_COLS WHERE FIELDSET_COLS_FIELDSET_ID=%s
        """
        db.query(sql, (rowid,))

        sql = """
        INSERT INTO FIELDSET_COLS(FIELDSET_COLS_FIELDSET_ID, FIELDSET_COLS_COL, FIELDSET_COLS_ORDER)
        VALUES (%s, %s, %s)
        """
        order = 0
        total = 0
        if cols:
            for col in cols:
                order += 1
                db.query(sql, (rowid, col, order))
                total += db.rowcount

        meta["rowcount"] = total
        db.commit()
        return haxdb.data.output(success=1, meta=meta, message="SAVED")

    @haxdb.app.route("/FIELDSET/delete", methods=["GET", "POST"])
    @haxdb.app.route("/FIELDSET/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_delete(rowid=None):
        return apis["FIELDSET"].delete_call(rowid=rowid)

    @haxdb.app.route("/QUERY/list", methods=["POST", "GET"])
    @haxdb.app.route("/QUERY/list/<context>", methods=["POST", "GET"])
    @haxdb.app.route("/QUERY/list/<context>/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_QUERY_list(context=None, context_id=0):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0
        people_id = haxdb.data.session.get("api_people_id")

        meta = {}
        meta["api"] = "QUERY"
        meta["action"] = "list"
        meta["context"] = context
        meta["context_id"] = context_id

        sql = """
        SELECT * FROM
        (
        SELECT * FROM QUERY WHERE QUERY_CONTEXT=%s and QUERY_CONTEXT_ID=%s AND
        QUERY_PEOPLE_ID IN (0,%s)
        ) F
        """
        params = (context, context_id, people_id)
        return apis["QUERY"].list_call(sql=sql, params=params)

    @haxdb.app.route("/QUERY/view", methods=["POST", "GET"])
    @haxdb.app.route("/QUERY/view/<int:rowid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_QUERY_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "QUERY"
        meta["action"] = "view"
        meta["rowid"] = rowid

        sql = """
        SELECT * FROM QUERY
        WHERE QUERY_ID=%s
        """
        params = (rowid,)
        return apis["QUERY"].view_call(sql, params, meta)

    @haxdb.app.route("/QUERY/save", methods=["GET", "POST"])
    @haxdb.app.route("/QUERY/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        return apis["QUERY"].save_call(rowid=rowid)

    @haxdb.app.route("/QUERY/new", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_new():
        context = haxdb.data.var.get("context")
        context_id = haxdb.data.var.get("context_id") or 0
        global_QUERY = haxdb.data.var.get("global") or 0

        people_id = 0
        if global_QUERY and global_QUERY == 1:
            people_id = haxdb.data.session.get("api_people_id")

        defaults = {
            "QUERY_CONTEXT": haxdb.data.var.get("context"),
            "QUERY_CONTEXT_ID": haxdb.data.var.get("context_id"),
            "QUERY_PEOPLE_ID": people_id
        }

        return apis["QUERY"].new_call(defaults=defaults)

    @haxdb.app.route("/QUERY/delete", methods=["GET", "POST"])
    @haxdb.app.route("/QUERY/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_QUERY_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "QUERY"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM QUERY WHERE QUERY_ID = %s"
        params = (rowid,)

        return apis["QUERY"].delete_call(sql, params, meta)
