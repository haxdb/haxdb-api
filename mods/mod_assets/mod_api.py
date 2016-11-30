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
    @haxdb.app.route("/ASSETS/list", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS/list/<path:query>", methods=["POST","GET"])
    def mod_assets_list(query=None):
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "list"
            
        sql = """
        SELECT *
        FROM ASSETS
        """
        params = ()
        return apis["ASSETS"].list_call(sql, params, data)
    
    
    @haxdb.app.route("/ASSETS/view", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS/view/<int:rowid>", methods=["POST","GET"])
    def mod_assets_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "view"
        data["input"]["rowid"] = rowid
           
        sql = """
        SELECT *
        FROM ASSETS
        WHERE ASSETS_ID=?
        """
        params = (rowid,)
        return apis["ASSETS"].view_call(sql, params, data)

    
    @haxdb.app.route("/ASSETS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS/new/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_new(name=None):
        name = name or haxdb.data.var.get("name")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "new"
        data["input"]["name"] = name
        data["input"]["qty"] = qty
        
        sql = "INSERT INTO ASSETS (ASSETS_NAME, ASSETS_QUANTITY, ASSETS_INTERNAL) VALUES (?, 1, 0)"
        params = (name, )
        
        return apis["ASSETS"].new_call(sql, params, data)

    @haxdb.app.route("/ASSETS/delete", methods=["GET","POST"])
    @haxdb.app.route("/ASSETS/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM ASSETS WHERE ASSETS_ID=? and ASSETS_INTERNAL!=1"
        params = (rowid,)
        
        return apis["ASSETS"].delete_call(sql, params, data)
        
    @haxdb.app.route("/ASSETS/save", methods=["GET","POST"])
    @haxdb.app.route("/ASSETS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_assets_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "save"
        data["input"]["column"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "ASSETS-%s-%s" % (rowid,col,)

        sql = "UPDATE ASSETS SET %s=? WHERE ASSETS_ID=? and ASSETS_INTERNAL!=1"
        params = (val,rowid,)
        return apis["ASSETS"].save_call(sql, params, data, col, val, rowid)
        

    @haxdb.app.route("/ASSET_LINKS/list", methods=["POST","GET"])
    @haxdb.app.route("/ASSET_LINKS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_asset_links_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "list"
        data["input"]["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=?"
        db.query(sql,(assets_id,))
        row = db.next()
        data["name"] = row["ASSETS_NAME"]

        sql = """
        SELECT ASSET_LINKS.*
        FROM ASSETS
        JOIN ASSET_LINKS ON ASSET_LINKS_ASSETS_ID=ASSETS_ID AND ASSETS_ID=?
        """
        params = (assets_id,)

        return apis["ASSET_LINKS"].list_call(sql, params, data)

    @haxdb.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>/<link>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_new(assets_id=None, name=None, link=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        name = name or haxdb.data.var.get("name")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "new"
        data["input"]["assets_id"] = assets_id
        data["input"]["name"] = name
        
        sql = "INSERT INTO ASSET_LINKS (ASSET_LINKS_ASSETS_ID, ASSET_LINKS_NAME, ASSET_LINKS_ORDER) "
        sql += "VALUES (?, ?, 999)"
        params = (assets_id, name,)
        return apis["ASSET_LINKS"].new_call(sql, params, data)
    
    @haxdb.app.route("/ASSET_LINKS/save", methods=["GET","POST"])
    @haxdb.app.route("/ASSET_LINKS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = col
        data["input"]["val"] = val
        data["oid"] = "ASSET_LINKS-%s-%s" % (rowid, col,)
        
        sql = "UPDATE ASSET_LINKS SET %s=? WHERE ASSET_LINKS_ID=?" 
        params = (val,rowid,)
        return apis["ASSET_LINKS"].save_call(sql, params, data, col, val, rowid)
    
    @haxdb.app.route("/ASSET_LINKS/delete", methods=["GET","POST"])
    @haxdb.app.route("/ASSET_LINKS/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM ASSET_LINKS WHERE ASSET_LINKS_ID=?"
        params = (rowid,)
        return apis["ASSET_LINKS"].delete_call(sql, params, data)
    
    @haxdb.app.route("/ASSET_AUTHS/list", methods=["POST","GET"])
    @haxdb.app.route("/ASSET_AUTHS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_ASSET_AUTHS_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_AUTHS"
        data["input"]["action"] = "list"
        data["input"]["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=?"
        db.query(sql,(assets_id,))
        row = db.next()
        data["name"] = row["ASSETS_NAME"]
        
        sql = """
        SELECT 
        ASSET_AUTHS.*, 
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST, PEOPLE_EMAIL
        FROM ASSET_AUTHS
        JOIN PEOPLE ON ASSET_AUTHS_PEOPLE_ID = PEOPLE_ID and ASSET_AUTHS_ASSETS_ID=?
        """
        params = (assets_id,)
        return apis["ASSET_AUTHS"].list_call(sql, params, data)

    @haxdb.app.route("/ASSET_AUTHS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_AUTHS/new/<int:assets_id>/<int:people_id>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_new(assets_id=None, people_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        people_id = people_id or haxdb.data.var.get("people_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_AUTHS"
        data["input"]["action"] = "new"
        data["input"]["assets_id"] = assets_id
        data["input"]["people_id"] = people_id
        
        sql = "INSERT INTO ASSET_AUTHS (ASSET_AUTHS_ASSETS_ID, ASSET_AUTHS_PEOPLE_ID) "
        sql += "VALUES (?, ?)"
        params = (assets_id, people_id,)
        return apis["ASSET_AUTHS"].new_call(sql, params, data)
    
    @haxdb.app.route("/ASSET_AUTHS/delete", methods=["GET","POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.app.route("/ASSET_AUTHS/delete/<int:assets_id>/<int:people_id>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_ASSET_AUTHS_delete(rowid=None, assets_id=None, people_id=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        people_id = people_id or haxdb.data.var.get("people_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_AUTHS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        data["input"]["assets_id"] = assets_id
        data["input"]["people_id"] = people_id
        
        if rowid:
            sql = "DELETE FROM ASSET_AUTHS WHERE ASSET_AUTHS_ID=?"
            params = (rowid,)
            
        elif assets_id and people_id:
            sql = "DELETE FROM ASSET_AUTH WHERE ASSET_AUTHS_ASSETS_ID=? and ASSET_AUTHS_PEOPLE_ID=?"
            params = (assets_id, people_id,)
            
        else:
            return haxdb.data.output(success=0, message="MISSING VALUES: rowid (or assets_id and people_id)")
        
        return apis["ASSET_AUTHS"].delete_call(sql, params, data)