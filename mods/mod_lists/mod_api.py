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
    @api.app.route("/LISTS/list", methods=["POST","GET"])
    @api.require_auth
    def mod_lists_list():
        query = api.data.get("query")
        name = api.data.get("name")
        rowid = api.data.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "LISTS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["name"] = name
        data["input"]["rowid"] = rowid
        
        if rowid:
            sql = "SELECT * FROM LISTS WHERE LISTS_ID = ?"
            db.query(sql, (rowid,))
        elif name:
            sql = "SELECT * FROM LISTS WHERE LISTS_NAME = ?"
            db.query(sql, (name,))
        elif query:
            query = "%" + query + "%"
            sql = "SELECT * FROM LISTS WHERE LISTS_NAME LIKE ?"
            db.query(sql, (query,))
        else:
            sql = "SELECT * FROM LISTS"
            db.query(sql)
    
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return api.output(success=1, rows=rows, data=data)

    @api.app.route("/LISTS/new", methods=["POST", "GET"])
    @api.app.route("/LISTS/new/<name>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_lists_new(name=None):
        name = name or api.data.get("name")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LISTS"
        data["input"]["action"] = "new"
        data["input"]["name"] = name
        
        sql = "INSERT INTO LISTS (LISTS_NAME,  LISTS_INTERNAL) VALUES (?, 0)"
        db.query(sql, (name,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    @api.app.route("/LISTS/delete", methods=["GET","POST"])
    @api.app.route("/LISTS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_lists_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "LISTS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM LISTS WHERE LISTS_ID=? and LISTS_INTERNAL!=1"
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN LIST ID OR LIST IS INTERNAL", data=data)
        
    @api.app.route("/LISTS/save", methods=["GET","POST"])
    @api.app.route("/LISTS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_lists_save (rowid=None, col=None, val=None):
        valid_cols = ["LISTS_NAME"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "LISTS"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["value"] = val
        data["oid"] = "LISTS-%s-%s" % (rowid,col,)

        if col not in valid_cols:
            return api.output(success=0, data=data, message="INVALID COLUMN")
        
        sql = "UPDATE LISTS SET LISTS_NAME=? WHERE LISTS_ID=? and LISTS_INTERNAL!=1"
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN rowid OR LIST IS INTERNAL", data=data)
    

    @api.app.route("/LIST_ITEMS/list", methods=["POST","GET"])
    @api.app.route("/LIST_ITEMS/list/<int:lists_id>", methods=["POST","GET"])
    @api.app.route("/LIST_ITEMS/list/<lists_name>", methods=["POST","GET"])
    @api.require_auth
    def mod_list_items_list(lists_id=None, lists_name=None):
        lists_id = lists_id or api.data.get("lists_id")
        lists_name = lists_name or api.data.get("lists_name")
        query = api.data.get("query")
        include_disabled = api.data.get("include_disabled")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LIST_ITEMS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["include_disabled"] = include_disabled
        data["input"]["lists_id"] = lists_id
        data["input"]["lists_name"] = lists_name

        if not lists_id and not lists_name:
            return api.output(success=0, data=data, message="MISSING VALUE: lists_id or lists_name")
        
        params = ()
        sql = "SELECT * FROM LISTS WHERE"
        if lists_id:
            sql += " LISTS_ID=?"
            params += (lists_id,)
        elif lists_name:
            sql += " LISTS_NAME=?"
            params += (lists_name,)
            
        db.query(sql,params)
        row = db.next()
        if not row:
            return api.output(success=0, data=data, message="UNKNOWN LIST")
        data["name"] = row["LISTS_NAME"]
        lists_id = row["LISTS_ID"]
        
        params = (lists_id,)
        sql = """
        SELECT * FROM LIST_ITEMS
        JOIN LISTS ON LIST_ITEMS_LISTS_ID = LISTS_ID
        WHERE
        LISTS_ID=?
        """
        
        if query:
            query = "%" + query + "%"
            sql += "and (LIST_ITEMS_VALUE LIKE ? OR LIST_ITEMS_DESCRIPTION LIKE ?)"
            params += (query,query,)
            
        if not include_disabled:
                sql += " AND LIST_ITEMS_ENABLED='1'"

        sql += " ORDER BY LIST_ITEMS_ORDER"
        db.query(sql,params)
        
        if db.error:
            return api.output(success=0, data=data, message=db.error)

        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return api.output(success=1, data=data, rows=rows)

    @api.app.route("/LIST_ITEMS/new", methods=["POST", "GET"])
    @api.app.route("/LIST_ITEMS/new/<int:lists_id>", methods=["POST", "GET"])
    @api.app.route("/LIST_ITEMS/new/<int:lists_id>/<name>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_list_items_new(lists_id=None, name=None):
        lists_id = lists_id or api.data.get("lists_id")
        name = name or api.data.get("name")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LIST_ITEMS"
        data["input"]["action"] = "new"
        data["input"]["lists_id"] = lists_id
        data["input"]["name"] = name
        
        sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) "
        sql += "VALUES (?, ?, ?, 0, 999)"
        db.query(sql, (lists_id, name, name,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    @api.app.route("/LIST_ITEMS/save", methods=["GET","POST"])
    @api.app.route("/LIST_ITEMS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_list_items_save (rowid=None, col=None, val=None):
        valid_cols = ["LIST_ITEMS_VALUE","LIST_ITEMS_DESCRIPTION","LIST_ITEMS_ENABLED","LIST_ITEMS_ORDER"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "LIST_ITEMS"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "LIST_ITEMS-%s-%s" % (rowid,col)
        
        if col not in valid_cols:
            return api.output(success=0, data=data, message="INVALID VALUE: col")
        
        if col == "LIST_ITEMS_ENABLED" and val not in ('0','1'):
            return api.output(success=0, data=data, message="INVALID VALUE: val")
        
        if col == "LIST_ITEMS_ORDER" and not tools.is_float(val):
            return api.output(success=0, data=data, message="INVALID VALUE: val")
        
        sql = "UPDATE LIST_ITEMS SET %s=? WHERE LIST_ITEMS_ID=?" % col
        db.query(sql, (val,rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID VALUE: rowid")        
    
    @api.app.route("/LIST_ITEMS/delete", methods=["GET","POST"])
    @api.app.route("/LIST_ITEMS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_list_items_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "LIST_ITEMS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid

        sql = "DELETE FROM LIST_ITEMS WHERE LIST_ITEMS_ID=?"
        db.query(sql, (rowid,))
        
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID VALUE: rowid")