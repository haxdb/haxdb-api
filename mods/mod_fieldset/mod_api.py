import mod_data
from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os, shlex

haxdb = None
db = None
config = None
apis = {}

def init(app_haxdb, app_db, app_config):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = app_db
    config = app_config

    for api_name in mod_data.apis:
        apis[api_name] = haxdb.api.api_call()
        apis[api_name].udf_context = mod_data.apis[api_name]["udf_context"]
        apis[api_name].udf_context_id = mod_data.apis[api_name]["udf_context_id"]
        apis[api_name].udf_rowid = mod_data.apis[api_name]["udf_rowid"]
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]
        
def run():
    @haxdb.app.route("/FIELDSET/list", methods=["POST","GET"])
    @haxdb.app.route("/FIELDSET/list/<context>", methods=["POST","GET"])
    @haxdb.app.route("/FIELDSET/list/<context>/<int:context_id>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_FIELDSET_list(context=None, context_id=0):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or 0
        
        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "list"
        meta["context"] = context
        meta["context_id"] = context_id

        sql = """
        SELECT * FROM 
        (SELECT * FROM FIELDSET WHERE context=%s and context_id=%s)
        """
        params = (context,context_id,)
        return apis["FIELDSET"].list_call(sql, params, meta)

    @haxdb.app.route("/FIELDSET/view", methods=["POST","GET"])
    @haxdb.app.route("/FIELDSET/view/<int:rowid>", methods=["POST","GET"])
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
    
    @haxdb.app.route("/FIELDSET/save", methods=["GET","POST"])
    @haxdb.app.route("/FIELDSET/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_save(rowid=None,col=None,val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "save"
        meta["rowid"] = rowid
        meta["col"] = col
        meta["val"] = val
        meta["oid"] = "FIELDSET-%s-%s" % (rowid,col)
        
        sql = "UPDATE FIELDSET SET {}=%s WHERE FIELDSET_ID=%s"
        params = (val, rowid)
        return apis["FIELDSET"].save_call(sql, params, meta, col, val, rowid)

    
    @haxdb.app.route("/FIELDSET/new", methods=["GET","POST"])
    @haxdb.app.route("/FIELDSET/new/<name>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_new(name=None):
        name = name or haxdb.data.var.get("name")
        
        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "new"
        meta["name"] = name

        if not name:
            return haxdb.data.output(success=0, message="MISSING INPUT: name", meta=meta)

        sql = "INSERT INTO FIELDSET (FIELDSET_NAME) VALUES (%s)"
        params = (name,)
        return apis["FIELDSET"].new_call(sql, params, meta)
    
    
    @haxdb.app.route("/FIELDSET/delete/", methods=["GET","POST"])
    @haxdb.app.route("/FIELDSET/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "delete"
        meta["rowid"] = rowid
        
        if not rowid:
            return haxdb.data.output(success=0, message="MISSING INPUT: rowid", meta=meta)
        
        sql = "DELETE FROM FIELDSET WHERE FIELDSET_ID = %s"
        db.query(sql,(rowid,))

        if db.rowcount > 0:
            db.commit();
            return haxdb.data.output(success=1, meta=meta)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", meta=meta)
    
    

    @haxdb.app.route("/FIELDSET/cols", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_FIELDSET_cols():
        rowid = haxdb.data.var.get("rowid")
        cols = haxdb.data.var.getlist("cols")

        meta = {}
        meta["api"] = "FIELDSET"
        meta["action"] = "cols"
        meta["rowid"] = rowid
        meta["cols"] = cols
        
        sql = """
        DELETE FROM FIELDSET_COLS WHERE FIELDSET_COLS_FIELDSET_ID=%s
        """
        db.query(sql,(rowid,))
        
        sql = """
        INSERT INTO FIELDSET_COLS(FIELDSET_COLS_FIELDSET_ID, FIELDSET_COLS_COL, FIELDSET_COLS_ORDER)
        VALUES (%s, %s, %s)
        """
        order = 0
        total = 0
        for col in cols:
            order += 1
            db.query(sql, (rowid, col, order))
            total += db.rowcount
        
        meta["rowcount"] = total
        return haxdb.data.output(success=1, meta=meta, message="SAVED")
        