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
        qty = haxdb.data.var.get("qty") or 1
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "new"
        data["input"]["name"] = name
        data["input"]["qty"] = qty
        
        sql = "INSERT INTO ASSETS (ASSETS_NAME, ASSETS_QUANTITY, ASSETS_INTERNAL) VALUES (?, ?, 0)"
        db.query(sql, (name, qty))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return haxdb.data.output(success=1, data=data, message="ASSET INSERTED")
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", data=data)

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
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN rowid OR ASSET IS INTERNAL", data=data)
        
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
        return apis["ASSETS"].save_call(sql, params, data, col, val)
        

    @haxdb.app.route("/ASSET_LINKS/list", methods=["POST","GET"])
    @haxdb.app.route("/ASSET_LINKS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_asset_links_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        query = haxdb.data.var.get("query")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=?"
        db.query(sql,(assets_id,))
        row = db.next()
        if not row:
            return haxdb.data.output(success=0, data=data, message="UNKNOWN ASSET")
        
        data["name"] = row["ASSETS_NAME"]
        
        if query:
            query = "%" + query + "%"
            sql = "SELECT * FROM ASSET_LINKS WHERE ASSET_LINKS_ASSETS_ID=? and (ASSET_LINKS_VALUE LIKE ? OR ASSET_LINKS_DESCRIPTION LIKE ?)"
            db.query(sql,(assets_id, query, query))
        else:
            sql = "SELECT * FROM ASSET_LINKS WHERE ASSET_LINKS_ASSETS_ID=?"
            db.query(sql,(assets_id,))
        
        row = db.next()
        rows = {}
        while row:
            rows[row["ASSET_LINKS_ID"]] = dict(row)
            row = db.next()
    
        return haxdb.data.output(success=1, data=data, rows=rows)

    @haxdb.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>/<link>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_new(assets_id=None, name=None, link=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        name = name or haxdb.data.var.get("name")
        link = link or haxdb.data.var.get("link") or ""
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "new"
        data["input"]["assets_id"] = assets_id
        data["input"]["name"] = name
        data["input"]["link"] = link
        
        sql = "INSERT INTO ASSET_LINKS (ASSET_LINKS_ASSETS_ID, ASSET_LINKS_NAME, ASSET_LINKS_LINK, ASSET_LINKS_ORDER) "
        sql += "VALUES (?, ?, ?, 999)"
        db.query(sql, (assets_id, name, link,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", data=data)

    @haxdb.app.route("/ASSET_LINKS/save", methods=["GET","POST"])
    @haxdb.app.route("/ASSET_LINKS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_asset_links_save (rowid=None, col=None, val=None):
        valid_cols = ["ASSET_LINKS_NAME","ASSET_LINKS_LINK","ASSET_LINKS_ORDER"]
        
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
        
        if col not in valid_cols:
            return haxdb.data.output(success=0, data=data, message="INVALID VALUE: col")
        
        if col == "ASSET_LINKS_ORDER" and not tools.is_float(val):
            return haxdb.data.output(success=0, data=data, message="INVALID VALUE: val")
        
        sql = "UPDATE ASSET_LINKS SET %s=? WHERE ASSET_LINKS_ID=?" % col
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="INVALID VALUE: rowid", data=data)
    
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
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="INVALID VALUE: rowid", data=data)
    
    @haxdb.app.route("/ASSET_AUTHS/list", methods=["POST","GET"])
    @haxdb.app.route("/ASSET_AUTHS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_ASSET_AUTHS_asset(assets_id=None):
        assets_id = assets_id or haxdb.data.var.get("assets_id")
        query = haxdb.data.var.get("query")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_AUTHS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["assets_id"] = assets_id

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=?"
        db.query(sql,(assets_id,))
        row = db.next()
        data["name"] = row["ASSETS_NAME"]
        
        sql = """
        SELECT 
        ASSET_AUTHS.*, PEOPLE_EMAIL, 
        FNAME.PEOPLE_COLUMN_VALUES_VALUE AS PEOPLE_FIRST_NAME, 
        LNAME.PEOPLE_COLUMN_VALUES_VALUE AS PEOPLE_LAST_NAME, 
        MEMB.PEOPLE_COLUMN_VALUES_VALUE AS PEOPLE_MEMBERSHIP
        FROM ASSET_AUTHS
        JOIN PEOPLE ON ASSET_AUTHS_PEOPLE_ID = PEOPLE_ID
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES FNAME ON FNAME.PEOPLE_COLUMN_VALUES_PEOPLE_ID=PEOPLE_ID AND FNAME.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES LNAME ON LNAME.PEOPLE_COLUMN_VALUES_PEOPLE_ID=PEOPLE_ID AND LNAME.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES MEMB ON MEMB.PEOPLE_COLUMN_VALUES_PEOPLE_ID=PEOPLE_ID AND MEMB.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='MEMBERSHIP')
        WHERE 
        ASSET_AUTHS_ASSETS_ID=?
        """
        params = (assets_id,)
        
        if query:
            query = "%" + query + "%"
            sql += """
            AND (
            PEOPLE_FIRST_NAME LIKE ?
            OR
            PEOPLE_LAST_NAME LIKE ?
            OR 
            PEOPLE_EMAIL LIKE ?
            OR 
            PEOPLE_MEMBERSHIP LIKE ?
            )
            """
            params += (query,query,query,query)

        sql += " ORDER BY PEOPLE_LAST_NAME, PEOPLE_FIRST_NAME"

        db.query(sql,params)
        
        if db.error:
            return haxdb.data.output(success=0, data=data, message=db.error)
        
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return haxdb.data.output(success=1, data=data, rows=rows)

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
        db.query(sql, (assets_id, people_id,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", data=data)

    
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
            db.query(sql, (rowid,))
            
        elif assets_id and people_id:
            sql = "DELETE FROM ASSET_AUTH WHERE ASSET_AUTHS_ASSETS_ID=? and ASSET_AUTHS_PEOPLE_ID=?"
            db.query(sql, (assets_id, people_id,))
            
        else:
            return haxdb.data.output(success=0, data=data, message="MISSING VALUES: rowid OR (assets_id and people_id)")
        
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="INVALID VALUE: rowid", data=data)    