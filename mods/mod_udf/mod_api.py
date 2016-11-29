import mod_data
from flask import request
from werkzeug.utils import secure_filename
import os

haxdb = None
db = None
config = None
tools = None
apis = {}

def init(app_haxdb, app_db, app_config, app_tools):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = app_tools

    for api_name in mod_data.apis:
        apis[api_name] = haxdb.api.api_call()
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]
        

def run():
    @haxdb.app.route("/UDF/list", methods=["POST","GET"])
    @haxdb.app.route("/UDF/list/<context>", methods=["POST","GET"])
    @haxdb.app.route("/UDF/list/<context>/<int:context_id>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_list(context=None, context_id=None):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or -1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF"
        data["input"]["action"] = "list"
        data["input"]["context"] = context
        data["input"]["context_id"] = context_id
            
        sql = """
        SELECT *
        FROM UDF
        JOIN UDF UDF2 ON UDF2.UDF_ID=UDF.UDF_ID AND UDF.UDF_CONTEXT=?
        """
        params = (context,)
        
        if context_id:
            sql += " and UDF.UDF_CONTEXT_ID=?"
            params += (int(context_id),)

        return apis["UDF"].list_call(sql, params, data)

    @haxdb.app.route("/UDF/categories", methods=["POST","GET"])
    @haxdb.app.route("/UDF/categories/<context>", methods=["POST","GET"])
    @haxdb.app.route("/UDF/categories/<context>/<int:context_id>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_categories(context=None, context_id=None):
        context = context or haxdb.data.var.get("context")
        context_id = context_id or haxdb.data.var.get("context_id") or -1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF"
        data["input"]["action"] = "categories"
        data["input"]["context"] = context
        data["input"]["context_id"] = context_id
            
        sql = """
        SELECT UDF.UDF_CATEGORY, UDF.UDF_NAME, UDF.UDF_TYPE, UDF.UDF_LISTS_ID
        FROM UDF
        JOIN (SELECT MUDF.UDF_CATEGORY, MIN(MUDF.UDF_ORDER) UDF_ORDER FROM UDF MUDF WHERE MUDF.UDF_ID=UDF_ID GROUP BY MUDF.UDF_CATEGORY) MUDF
        WHERE
        UDF.UDF_CONTEXT=? and UDF.UDF_CONTEXT_ID=?
        AND UDF_ENABLED=1
        GROUP BY UDF.UDF_ID, UDF.UDF_CATEGORY, UDF.UDF_NAME, UDF.UDF_TYPE, UDF.UDF_LISTS_ID, UDF.UDF_ORDER
        ORDER BY MUDF.UDF_ORDER, UDF.UDF_CATEGORY
        """ 
        params = (context, context_id)
        
        db.query(sql,params)
        if db.error:
            return haxdb.data.output(success=0, data=data, message=db.error)
        
        data["rows"] = {}
        row = db.next()
        while row:
            c = row["UDF_CATEGORY"]
            if c not in data["rows"]:
                data["rows"][c] = []
            data["rows"][c].append(dict(row))
            row = db.next()
            
        return haxdb.data.output(success=1, data=data)
    
    @haxdb.app.route("/UDF/new", methods=["POST", "GET"])
    @haxdb.app.route("/UDF/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_new(name=None):
        name = name or haxdb.data.var.get("name")
        context = haxdb.data.var.get("context")
        context_id = haxdb.data.var.get("context_id") or -1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF"
        data["input"]["action"] = "new"
        data["input"]["name"] = name
        data["input"]["context"] = context
        data["input"]["context_id"] = context_id
        
        sql = """
        INSERT INTO UDF (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_CATEGORY, UDF_NAME, UDF_TYPE, UDF_ORDER, UDF_KEY, UDF_ENABLED, UDF_INTERNAL) 
        VALUES (?, ?, "NEW CATEGORY", ?, "TEXT", 999, 0, 0, 0)
        """
        params = (context, context_id, name,)
        return apis["UDF"].new_call(sql, params, data)
    

    @haxdb.app.route("/UDF/delete", methods=["GET","POST"])
    @haxdb.app.route("/UDF/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM UDF WHERE UDF_ID=? and UDF_INTERNAL!=1"
        params = (rowid,)
        return apis["UDF"].delete_call(sql, params, data)
        
    @haxdb.app.route("/UDF/save", methods=["GET","POST"])
    @haxdb.app.route("/UDF/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF"
        data["input"]["action"] = "save"
        data["input"]["column"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "UDF-%s-%s" % (rowid,col,)

        sql = "UPDATE UDF SET %s=? WHERE UDF_ID=? and UDF_INTERNAL!=1"
        params = (val,rowid,)
        return apis["UDF"].save_call(sql, params, data, col, val)
        
