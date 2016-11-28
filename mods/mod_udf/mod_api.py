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
    @haxdb.app.route("/UDF_DEF/list", methods=["POST","GET"])
    @haxdb.app.route("/UDF_DEF/list/<context>/<int:id1>/<int:id2>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_list(context=None, id1=None, id2=None):
        context = context or haxdb.data.var.get("context")
        id1 = id1 or haxdb.data.var.get("id1") or -1
        id2 = id2 or haxdb.data.var.get("id2") or -1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF_DEF"
        data["input"]["action"] = "list"
        data["input"]["context"] = context
        data["input"]["id1"] = id1
        data["input"]["id2"] = id2
            
        sql = """
        SELECT *
        FROM UDF_DEF
        WHERE
        UDF_DEF_CONTEXT=?
        """
        params = (context,)
        
        if id1:
            sql += " and UDF_DEF_CONTEXT_ID1=?"
            params += (int(id1),)

        if id2:
            sql += " and UDF_DEF_CONTEXT_ID2=?"
            params += (int(id2),)
        
        return apis["UDF_DEF"].list_call(sql, params, data)
    
    
    @haxdb.app.route("/UDF_DEF/new", methods=["POST", "GET"])
    @haxdb.app.route("/UDF_DEF/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_new(name=None):
        name = name or haxdb.data.var.get("name")
        context = haxdb.data.var.get("context")
        id1 = haxdb.data.var.get("id1") or -1
        id2 = haxdb.data.var.get("id2") or -1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF_DEF"
        data["input"]["action"] = "new"
        data["input"]["name"] = name
        data["input"]["context"] = context
        data["input"]["id1"] = id1
        data["input"]["id2"] = id2
        
        sql = """
        INSERT INTO UDF_DEF (UDF_DEF_CONTEXT, UDF_DEF_CONTEXT_ID1, UDF_DEF_CONTEXT_ID2, UDF_DEF_CATEGORY, UDF_DEF_NAME, UDF_DEF_TYPE, UDF_DEF_ORDER, UDF_DEF_KEY, UDF_DEF_ENABLED, UDF_DEF_INTERNAL) 
        VALUES (?, ?, ?, "NEW CATEGORY", ?, "TEXT", 999, 0, 0, 0)
        """
        params = (context, id1, id2, name,)
        return apis["UDF_DEF"].new_call(sql, params, data)
    

    @haxdb.app.route("/UDF_DEF/delete", methods=["GET","POST"])
    @haxdb.app.route("/UDF_DEF/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF_DEF"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM UDF_DEF WHERE UDF_DEF_ID=? and UDF_DEF_INTERNAL!=1"
        params = (rowid,)
        return apis["UDF_DEF"].delete_call(sql, params, data)
        
    @haxdb.app.route("/UDF_DEF/save", methods=["GET","POST"])
    @haxdb.app.route("/UDF_DEF/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.no_readonly
    @haxdb.require_dba
    def mod_udf_def_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "UDF_DEF"
        data["input"]["action"] = "save"
        data["input"]["column"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "UDF_DEF-%s-%s" % (rowid,col,)

        sql = "UPDATE UDF_DEF SET %s=? WHERE UDF_DEF_ID=? and UDF_DEF_INTERNAL!=1"
        params = (val,rowid,)
        return apis["UDF_DEF"].save_call(sql, params, data, col, val)
        
