import mod_data
from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os, shlex

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
        apis[api_name].udf_context = mod_data.apis[api_name]["udf_context"]
        apis[api_name].udf_context_id = mod_data.apis[api_name]["udf_context_id"]
        apis[api_name].udf_rowid = mod_data.apis[api_name]["udf_rowid"]
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]
        
def run():
    @haxdb.app.route("/PEOPLE/list", methods=["POST","GET"])
    @haxdb.app.route("/PEOPLE/list/<int:category>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_list(category=None):
       
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "list"
        data["input"]["category"] = category

        sql = """
        SELECT * FROM LISTS
        JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID
        WHERE 
        LIST_ITEMS_ENABLED=1
        and LISTS_ID IN (SELECT UDF_LISTS_ID FROM UDF WHERE UDF_CONTEXT='PEOPLE' and UDF_CONTEXT_ID = 0)
        ORDER BY LIST_ITEMS_ORDER
        """
        data["lists"] = {}
        db.query(sql)
        row = db.next()
        while row:
            if row["LISTS_NAME"] not in data["lists"]:
                data["lists"][row["LISTS_NAME"]] = []
            data["lists"][row["LISTS_NAME"]].append(dict(row))
            row = db.next()
        
        sql = """
        SELECT * FROM PEOPLE
        """
        params = ()
        return apis["PEOPLE"].list_call(sql, params, data)

    @haxdb.app.route("/PEOPLE/view", methods=["POST","GET"])
    @haxdb.app.route("/PEOPLE/view/<int:rowid>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "view"
        data["input"]["rowid"] = rowid
        
        sql = """
        SELECT * FROM PEOPLE
        WHERE PEOPLE_ID=?
        """
        params = (rowid,)
        return apis["PEOPLE"].view_call(sql, params, data)
    
    @haxdb.app.route("/PEOPLE/save", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_save(rowid=None,col=None,val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = col
        data["input"]["val"] = val
        data["oid"] = "PEOPLE-%s-%s" % (rowid,col)
        
        sql = "UPDATE PEOPLE SET %s=? WHERE PEOPLE_ID=?"
        params = (val, rowid)
        return apis["PEOPLE"].save_call(sql, params, data, col, val, rowid)

    
    @haxdb.app.route("/PEOPLE/new", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/new/<email>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_new(email=None):
        email = email or haxdb.data.var.get("email")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "new"
        data["input"]["email"] = email

        if not email:
            return haxdb.data.output(success=0, message="MISSING INPUT: email", data=data)

        sql = "INSERT INTO PEOPLE (PEOPLE_EMAIL,PEOPLE_DBA) VALUES (?,0)"
        db.query(sql,(email,))

        if db.rowcount > 0:
            data["rowid"] = db.lastrowid
            db.commit()
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", data=data)
    
    @haxdb.app.route("/PEOPLE/delete/", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        if not rowid:
            return haxdb.data.output(success=0, message="MISSING INPUT: rowid", data=data)
        
        sql = "DELETE FROM PEOPLE WHERE PEOPLE_ID = ?"
        db.query(sql,(rowid,))

        if db.rowcount > 0:
            db.commit();
            return haxdb.data.output(success=1, data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", data=data)
    
    
