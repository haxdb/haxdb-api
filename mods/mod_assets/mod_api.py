from flask import request
from werkzeug.utils import secure_filename
import os

api = None
db = None
config = None
tools = None

def init(app_api, app_db, app_config, app_tools):
    global api, db, config, tools
    api = app_api
    db = app_db
    config = app_config
    tools = app_tools

def run():
    @api.app.route("/ASSETS/list", methods=["POST","GET"])
    @api.app.route("/ASSETS/list/<path:query>", methods=["POST","GET"])
    def mod_assets_list(query=None):
        query = query or api.var.get("query")
    
        query_cols = ["ASSETS_ID","ASSETS_LOCATION","ASSETS_NAME","ASSETS_MANUFACTURER","ASSETS_PRODUCT_ID","ASSETS_SERIAL_NUMBER"]
        search_cols = ["ASSETS_NAME","ASSETS_LOCATION","ASSETS_TYPE","ASSETS_MANUFACTURER","ASSETS_PRODUCT_ID","ASSETS_SERIAL_NUMBER"]
        order_cols = ["ASSETS_LOCATION","ASSETS_NAME"]
        lists = ["ASSET STATUSES", "ASSET LOCATIONS"]
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
            
        sql = """
        SELECT *
        FROM ASSETS
        WHERE 1=1
        """

        return api.api_list(data,sql,query,query_cols,search_cols,order_cols,lists)
    
    
    @api.app.route("/ASSETS/view", methods=["POST","GET"])
    @api.app.route("/ASSETS/view/<int:rowid>", methods=["POST","GET"])
    def mod_assets_view(rowid=None):
        lists = ["ASSET STATUSES", "ASSET LOCATIONS"]
        
        rowid = rowid or api.var.get("rowid")
        
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
        return api.api_view(data, sql, params, lists)
    
    @api.app.route("/ASSETS/new", methods=["POST", "GET"])
    @api.app.route("/ASSETS/new/<name>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_new(name=None):
        name = name or api.var.get("name")
        qty = api.var.get("qty") or 1
        
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
            return api.output(success=1, data=data, message="ASSET INSERTED")
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    @api.app.route("/ASSETS/delete", methods=["GET","POST"])
    @api.app.route("/ASSETS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_delete(rowid=None):
        rowid = rowid or api.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM ASSETS WHERE ASSETS_ID=? and ASSETS_INTERNAL!=1"
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN rowid OR ASSET IS INTERNAL", data=data)
        
    @api.app.route("/ASSETS/save", methods=["GET","POST"])
    @api.app.route("/ASSETS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_save (rowid=None, col=None, val=None):
        valid_cols = {
            "ASSETS_NAME": "STR",
            "ASSETS_TYPE": "STR",
            "ASSETS_REQUIRE_AUTH": "STR",
            "ASSETS_AUTO_LOG": "BOOL",
            "ASSETS_MANUFACTURER": "STR",
            "ASSETS_PRODUCT_ID": "STR",
            "ASSETS_SERIAL_NUMBER": "STR",
            "ASSETS_QUANTITY": "INT",
            "ASSETS_LOCATION": "STR",
            "ASSETS_DESCRIPTION": "STR",
            "ASSETS_STATUS": "STR",
            "ASSETS_STATUS_DESCRIPTION": "STR"
        }
        
        rowid = rowid or api.var.get("rowid")
        col = col or api.var.get("col")
        val = val or api.var.get("val")
        
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
        return api.api_save(data,sql,params,col,val,valid_cols)
        

    @api.app.route("/ASSET_LINKS/list", methods=["POST","GET"])
    @api.app.route("/ASSET_LINKS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_asset_links_asset(assets_id=None):
        assets_id = assets_id or api.var.get("assets_id")
        query = api.var.get("query")

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
            return api.output(success=0, data=data, message="UNKNOWN ASSET")
        
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
    
        return api.output(success=1, data=data, rows=rows)

    @api.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @api.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>", methods=["POST", "GET"])
    @api.app.route("/ASSET_LINKS/new/<int:assets_id>/<name>/<link>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_new(assets_id=None, name=None, link=None):
        assets_id = assets_id or api.var.get("assets_id")
        name = name or api.var.get("name")
        link = link or api.var.get("link") or ""
        
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
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    @api.app.route("/ASSET_LINKS/save", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_save (rowid=None, col=None, val=None):
        valid_cols = ["ASSET_LINKS_NAME","ASSET_LINKS_LINK","ASSET_LINKS_ORDER"]
        
        rowid = rowid or api.var.get("rowid")
        col = col or api.var.get("col")
        val = val or api.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = col
        data["input"]["val"] = val
        data["oid"] = "ASSET_LINKS-%s-%s" % (rowid, col,)
        
        if col not in valid_cols:
            return api.output(success=0, data=data, message="INVALID VALUE: col")
        
        if col == "ASSET_LINKS_ORDER" and not tools.is_float(val):
            return api.output(success=0, data=data, message="INVALID VALUE: val")
        
        sql = "UPDATE ASSET_LINKS SET %s=? WHERE ASSET_LINKS_ID=?" % col
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID VALUE: rowid", data=data)
    
    @api.app.route("/ASSET_LINKS/delete", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_delete(rowid=None):
        rowid = rowid or api.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM ASSET_LINKS WHERE ASSET_LINKS_ID=?"
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID VALUE: rowid", data=data)
    
    @api.app.route("/ASSET_AUTHS/list", methods=["POST","GET"])
    @api.app.route("/ASSET_AUTHS/list/<int:assets_id>", methods=["POST","GET"])
    def mod_ASSET_AUTHS_asset(assets_id=None):
        assets_id = assets_id or api.var.get("assets_id")
        query = api.var.get("query")

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
            return api.output(success=0, data=data, message=db.error)
        
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return api.output(success=1, data=data, rows=rows)

    @api.app.route("/ASSET_AUTHS/new", methods=["POST", "GET"])
    @api.app.route("/ASSET_AUTHS/new/<int:assets_id>/<int:people_id>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_ASSET_AUTHS_new(assets_id=None, people_id=None):
        assets_id = assets_id or api.var.get("assets_id")
        people_id = people_id or api.var.get("people_id")
        
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
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    
    @api.app.route("/ASSET_AUTHS/delete", methods=["GET","POST"])
    @api.app.route("/ASSET_AUTHS/delete/<int:rowid>", methods=["GET","POST"])
    @api.app.route("/ASSET_AUTHS/delete/<int:assets_id>/<int:people_id>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_ASSET_AUTHS_delete(rowid=None, assets_id=None, people_id=None):
        rowid = rowid or api.var.get("rowid")
        assets_id = assets_id or api.var.get("assets_id")
        people_id = people_id or api.var.get("people_id")

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
            return api.output(success=0, data=data, message="MISSING VALUES: rowid OR (assets_id and people_id)")
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID VALUE: rowid", data=data)    