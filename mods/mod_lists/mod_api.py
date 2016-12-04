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
    global haxdb, db, config, tools
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
    @haxdb.app.route("/LISTS/list", methods=["POST","GET"])
    @haxdb.require_auth
    def mod_lists_list():
        meta = {}
        meta["api"] = "LISTS"
        meta["action"] = "list"
        
        sql = "SELECT * FROM LISTS"
        params = ()
        return apis["LISTS"].list_call(sql, params, meta)
    
    @haxdb.app.route("/LISTS/new", methods=["POST", "GET"])
    @haxdb.app.route("/LISTS/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_new(name=None):
        name = name or haxdb.data.var.get("name")
        
        
        meta = {}
        meta["api"] = "LISTS"
        meta["action"] = "new"
        meta["name"] = name
        
        sql = "INSERT INTO LISTS (LISTS_NAME,  LISTS_INTERNAL) VALUES (%s, 0)"
        params = (name,)
        return apis["LISTS"].new_call(sql, params, meta)

    @haxdb.app.route("/LISTS/delete", methods=["GET","POST"])
    @haxdb.app.route("/LISTS/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        
        meta = {}
        meta["api"] = "LISTS"
        meta["action"] = "delete"
        meta["rowid"] = rowid
        
        sql = "DELETE FROM LISTS WHERE LISTS_ID=%s and LISTS_INTERNAL!=1"
        params = (rowid,)
        return apis["LISTS"].delete_call(sql, params, meta)
        
    @haxdb.app.route("/LISTS/save", methods=["GET","POST"])
    @haxdb.app.route("/LISTS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_lists_save (rowid=None, col=None, val=None):
        valid_cols = ["LISTS_NAME"]
        
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")

        
        meta = {}
        meta["api"] = "LISTS"
        meta["action"] = "save"
        meta["col"] = col
        meta["rowid"] = rowid
        meta["value"] = val
        meta["oid"] = "LISTS-%s-%s" % (rowid,col,)

        sql = "UPDATE LISTS SET {}=%s WHERE LISTS_ID=%s and LISTS_INTERNAL!=1"
        params = (val,rowid,)
        return apis["LISTS"].save_call(sql, params, meta, col, val, rowid)
    

    @haxdb.app.route("/LIST_ITEMS/list", methods=["POST","GET"])
    @haxdb.app.route("/LIST_ITEMS/list/<int:lists_id>", methods=["POST","GET"])
    @haxdb.app.route("/LIST_ITEMS/list/<lists_name>", methods=["POST","GET"])
    @haxdb.require_auth
    def mod_list_items_list(lists_id=None, lists_name=None):
        lists_id = lists_id or haxdb.data.var.get("lists_id")
        lists_name = lists_name or haxdb.data.var.get("lists_name")
        query = haxdb.data.var.get("query")
        include_disabled = haxdb.data.var.get("include_disabled")
        
        
        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "list"
        meta["query"] = query
        meta["include_disabled"] = include_disabled
        meta["lists_id"] = lists_id

        if not lists_id and not lists_name:
            return haxdb.data.output(success=0, meta=meta, message="MISSING VALUE: lists_id or lists_name")

        meta["lists_name"] = lists_name
        if lists_id:
            row = db.qaf("SELECT * FROM LISTS WHERE LISTS_ID=%s", (lists_id,))
            meta["lists_name"] = row["LISTS_NAME"]
            
        sql = """
            SELECT
            *
            FROM LIST_ITEMS
            JOIN LISTS ON LIST_ITEMS_LISTS_ID=LISTS_ID
        """
        params = ()
        if lists_id:
            sql += " AND LISTS_ID=%s"
            params += (lists_id,)
        elif lists_name:
            sql += " AND LISTS_NAME=%s"
            params += (lists_name,)

        return apis["LIST_ITEMS"].list_call(sql, params, meta)
    
    @haxdb.app.route("/LIST_ITEMS/new", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:lists_id>", methods=["POST", "GET"])
    @haxdb.app.route("/LIST_ITEMS/new/<int:lists_id>/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_new(lists_id=None, name=None):
        lists_id = lists_id or haxdb.data.var.get("lists_id")
        name = name or haxdb.data.var.get("name")
        
        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "new"
        meta["lists_id"] = lists_id
        meta["name"] = name
        
        sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) "
        sql += "VALUES (%s, %s, %s, 0, 999)"
        params = (lists_id, name, name,)
        return apis["LIST_ITEMS"].new_call(sql, params, meta)
    
    @haxdb.app.route("/LIST_ITEMS/save", methods=["GET","POST"])
    @haxdb.app.route("/LIST_ITEMS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")

        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "save"
        meta["col"] = col
        meta["rowid"] = rowid
        meta["val"] = val
        meta["oid"] = "LIST_ITEMS-%s-%s" % (rowid,col)
        
        sql = "UPDATE LIST_ITEMS SET {}=%s WHERE LIST_ITEMS_ID=%s"
        params = (val, rowid,)
        return apis["LIST_ITEMS"].save_call(sql,params,meta,col,val)
        
        
    
    @haxdb.app.route("/LIST_ITEMS/delete", methods=["GET","POST"])
    @haxdb.app.route("/LIST_ITEMS/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_list_items_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        meta = {}
        meta["api"] = "LIST_ITEMS"
        meta["action"] = "delete"
        meta["rowid"] = rowid

        sql = "DELETE FROM LIST_ITEMS WHERE LIST_ITEMS_ID=%s"
        params = (rowid,)
        return apis["LIST_ITEMS"].delete_call(sql, params, meta)