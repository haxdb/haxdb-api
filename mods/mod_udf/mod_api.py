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
    @haxdb.app.route("/UDF/list", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/list/<context>", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/list/<context>/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_list(context=None, context_id=None):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0

        try:
            disabled = int(haxdb.data.var.get("disabled"))
        except:
            disabled = 0

        if disabled == 1:
            sql = """
            SELECT *
            FROM ( SELECT * FROM UDF U2 WHERE U2.UDF_CONTEXT=%s AND U2.UDF_CONTEXT_ID=%s) UDF2
            """
        else:
            sql = """
            SELECT *
            FROM ( SELECT * FROM UDF U2 WHERE U2.UDF_CONTEXT=%s AND U2.UDF_CONTEXT_ID=%s AND U2.UDF_ENABLED=1 ) UDF2
            """
        params = (context, context_id,)

        return apis["UDF"].list_call(sql=sql, params=params)

    @haxdb.app.route("/UDF/categories", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/categories/<context>", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/categories/<context>/<int:context_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_categories(context=None, context_id=None):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0

        meta = {}
        meta["api"] = "UDF"
        meta["action"] = "categories"
        meta["context"] = context
        meta["context_id"] = context_id

        sql = """
                SELECT x.UDF_CATEGORY, x.UDF_NAME, x.UDF_TYPE, x.UDF_LISTS_ID, MINORDER, x.UDF_ORDER
                FROM UDF x
                JOIN (SELECT UDF_CATEGORY, MIN(UDF_ORDER) MINORDER FROM UDF WHERE UDF_ENABLED=1 GROUP BY UDF_CATEGORY) y
                WHERE
                y.UDF_CATEGORY=x.UDF_CATEGORY
                AND x.UDF_CONTEXT=%s and x.UDF_CONTEXT_ID=%s
                AND x.UDF_ENABLED=1
                ORDER BY MINORDER, x.UDF_CATEGORY, x.UDF_ORDER
                """
        params = (context, context_id)

        db.query(sql, params)
        if db.error:
            return haxdb.data.output(success=0, meta=meta, message=db.error)

        rows = []
        row = db.next()
        lastcat = None
        cat = []
        while row:
            if lastcat != row["UDF_CATEGORY"]:
                if lastcat:
                    rows.append(cat)
                cat = []
                lastcat = row["UDF_CATEGORY"]

            cat.append(dict(row))
            row = db.next()
        if cat:
            rows.append(cat)

        return haxdb.data.output(success=1, meta=meta, data=rows)

    @haxdb.app.route("/UDF/new", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_new(name=None):
        name = name or haxdb.data.var.get("name")
        context = haxdb.data.var.get("context")
        context_id = haxdb.data.var.get("context_id") or 0
        category = haxdb.data.var.get("category") or "NEW CATEGORY"
        order = haxdb.data.var.get("order") or 999

        meta = {}
        meta["api"] = "UDF"
        meta["action"] = "new"
        meta["category"] = category
        meta["name"] = name
        meta["context"] = context
        meta["context_id"] = context_id

        sql = """
        INSERT INTO UDF (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_CATEGORY, UDF_NAME, UDF_TYPE, UDF_ORDER, UDF_KEY, UDF_ENABLED, UDF_INTERNAL)
        VALUES (%s, %s, %s, %s, "TEXT", %s, 0, 0, 0)
        """
        params = (context, context_id, category, name, order)
        return apis["UDF"].new_call(sql, params, meta)

    @haxdb.app.route("/UDF/delete", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/delete/<int:rowid>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "UDF"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM UDF WHERE UDF_ID=%s and UDF_INTERNAL!=1"
        params = (rowid,)
        return apis["UDF"].delete_call(sql, params, meta)

    @haxdb.app.route("/UDF/save", methods=["GET", "POST"])
    @haxdb.app.route("/UDF/save/<int:rowid>/<col>/<val>", methods=["GET", "POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")

        meta = {}
        meta["api"] = "UDF"
        meta["action"] = "save"
        meta["column"] = col
        meta["rowid"] = rowid
        meta["val"] = val
        meta["oid"] = "UDF-%s-%s" % (rowid, col,)

        if col in ("UDF_ORDER", "UDF_CATEGORY", "UDF_ENABLED"):
            sql = "UPDATE UDF SET {}=%s WHERE UDF_ID=%s"
        else:
            sql = "UPDATE UDF SET {}=%s WHERE UDF_ID=%s and UDF_INTERNAL!=1"
        params = (val, rowid,)
        return apis["UDF"].save_call(sql, params, meta, col, val)
