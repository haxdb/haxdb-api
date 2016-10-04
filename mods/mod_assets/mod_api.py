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
    def mod_assets_list():
        query = api.data.get("query")
        location = api.data.get("location")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["location"] = location
        
        sql = """
        SELECT ASSETS.*, LIST_ITEMS_NAME AS ASSETS_LOCATION_NAME FROM ASSETS
        LEFT OUTER JOIN LIST_ITEMS ON LIST_ITEMS_ID=ASSETS_LOCATION_LIST_ITEMS_ID
        """
        if location:
            if query:
                query = "%" + query + "%"
                sql += " WHERE ASSETS_LOCATION_LIST_ITEMS_ID = ? and (ASSETS_NAME LIKE ? or LIST_ITEMS_NAME LIKE ?)"
                sql += " ORDER BY LIST_ITEMS_VALUE, ASSETS_NAME"
                db.query(sql, (location, query, query,))
            else:
                sql += " WHERE ASSETS_LOCATION_LIST_ITEMS_ID = ?"
                sql += " ORDER BY LIST_ITEMS_VALUE, ASSETS_NAME"
                print sql
                db.query(sql, (location,))
        else:
            if query:
                query = "%" + query + "%"
                sql += " WHERE ASSETS_NAME LIKE ? OR LIST_ITEMS_NAME LIKE ?"
                sql += " ORDER BY LIST_ITEMS_VALUE, ASSETS_NAME"
                db.query(sql, (query, query))
            else:
                sql += " ORDER BY LIST_ITEMS_VALUE, ASSETS_NAME"
                db.query(sql)
                
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return api.output(success=1, data=data, rows=rows)

    @api.app.route("/ASSETS/new", methods=["POST", "GET"])
    @api.app.route("/ASSETS/new/<name>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_new(name=None):
        name = name or api.data.get("name")
        qty = api.data.get("qty") or 1
        
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
            return api.output(success=1, data=data, info="ASSET INSERTED")
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="UNKNOWN ERROR", data=data)

    @api.app.route("/ASSETS/delete", methods=["GET","POST"])
    @api.app.route("/ASSETS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")

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
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="UNKNOWN ASSET ID OR ASSET IS INTERNAL", data=data)
        
    @api.app.route("/ASSETS/save", methods=["GET","POST"])
    @api.app.route("/ASSETS/save/<int:rowid>", methods=["GET","POST"])
    @api.app.route("/ASSETS/save/<int:rowid>/<col>", methods=["GET","POST"])
    @api.app.route("/ASSETS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_assets_save (rowid=None, col=None, val=None):
        valid_cols = ["ASSETS_NAME","ASSETS_TYPE","ASSETS_REQUIRE_AUTH","ASSETS_AUTO_LOG","ASSETS_MANUFACTURER","ASSETS_PRODUCT_ID","ASSETS_SERIAL_NUMBER","ASSETS_QUANTITY","ASSETS_LOCATION_LIST_ITEMS_ID","ASSETS_AREA_LISTS_ID","ASSETS_DESCRIPTION"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS"
        data["input"]["action"] = "save"
        data["input"]["column"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "ASSETS-%s-%s" % (rowid,col,)
        
        if col not in valid_cols:
            return api.output(success=0, data=data, info="INVALID VALUE: col")
        
        sql = "UPDATE ASSETS SET %s=? WHERE ASSETS_ID=? and ASSETS_INTERNAL!=1" % (col)
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, data=data, info="INVALID ASSET ID OR ASSET IS INTERNAL")
    

    @api.app.route("/ASSET_LINKS/list", methods=["POST","GET"])
    @api.app.route("/ASSET_LINKS/list/<int:rowid>", methods=["POST","GET"])
    def mod_asset_links_asset(rowid=None):
        rowid = rowid or api.data.get("rowid")
        query = api.data.get("query")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["rowid"] = rowid

        sql = "SELECT * FROM ASSETS WHERE ASSETS_ID=?"
        db.query(sql,(rowid,))
        row = db.next()
        data["name"] = row["ASSETS_NAME"]
        
        if query:
            query = "%" + query + "%"
            sql = "SELECT * FROM ASSET_LINKS WHERE ASSET_LINKS_ASSETS_ID=? and (ASSET_LINKS_VALUE LIKE ? OR ASSET_LINKS_DESCRIPTION LIKE ?)"
            db.query(sql,(rowid, query, query))
        else:
            sql = "SELECT * FROM ASSET_LINKS WHERE ASSET_LINKS_ASSETS_ID=?"
            db.query(sql,(rowid,))
        
        row = db.next()
        rows = {}
        while row:
            rows[row["ASSET_LINKS_ID"]] = dict(row)
            row = db.next()
    
        return api.output(success=1, data=data, rows=rows)

    @api.app.route("/ASSET_LINKS/new", methods=["POST", "GET"])
    @api.app.route("/ASSET_LINKS/new/<int:rowid>", methods=["POST", "GET"])
    @api.app.route("/ASSET_LINKS/new/<int:rowid>/<name>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_new(rowid=None, name=None):
        rowid = rowid or api.data.get("rowid")
        name = name or api.data.get("name")
        link = api.data.get("link") or ""
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "new"
        data["input"]["rowid"] = rowid
        data["input"]["name"] = name
        data["input"]["link"] = link
        
        sql = "INSERT INTO ASSET_LINKS (ASSET_LINKS_ASSETS_ID, ASSET_LINKS_NAME, ASSET_LINKS_LINK, ASSET_LINKS_ORDER) "
        sql += "VALUES (?, ?, ?, 999)"
        db.query(sql, (rowid, name, link,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="UNKNOWN ERROR", data=data)

    @api.app.route("/ASSET_LINKS/save", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/save/<int:rowid>", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/save/<int:rowid>/<col>", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_save (rowid=None, col=None, val=None):
        valid_cols = ["ASSET_LINKS_NAME","ASSET_LINKS_LINK","ASSET_LINKS_ORDER"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSET_LINKS"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = col
        data["input"]["val"] = val
        data["oid"] = "ASSET_LINKS-%s-%s" % (rowid, col,)
        
        if col not in valid_cols:
            return api.output(success=0, data=data, info="INVALID VALUE: col")
        
        if col == "ASSET_LINKS_ORDER" and not tools.is_float(val):
            return api.output(success=0, data=data, info="INVALID VALUE: val")
        
        sql = "UPDATE ASSET_LINKS SET %s=? WHERE ASSET_LINKS_ID=?" % col
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="INVALID VALUE: rowid", data=data)
    
    @api.app.route("/ASSET_LINKS/delete", methods=["GET","POST"])
    @api.app.route("/ASSET_LINKS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_asset_links_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")

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
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="INVALID VALUE: rowid", data=data)