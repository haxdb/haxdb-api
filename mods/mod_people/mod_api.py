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
       
        
        meta = {}
        meta["api"] = "PEOPLE"
        meta["action"] = "list"
        meta["category"] = category

        """
        sql = "SELECT * FROM LISTS ORDER BY LISTS_NAME"
        apis["PEOPLE"].lists = []
        db.query(sql)
        row = db.next()
        while row:
            apis["PEOPLE"].lists.append(row["LISTS_NAME"])
            row = db.next()
        """
        
        sql = """
        SELECT * FROM PEOPLE
        """
        params = ()
        return apis["PEOPLE"].list_call(sql, params, meta)

    @haxdb.app.route("/PEOPLE/view", methods=["POST","GET"])
    @haxdb.app.route("/PEOPLE/view/<int:rowid>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_people_view(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        meta = {}
        meta["api"] = "PEOPLE"
        meta["action"] = "view"
        meta["rowid"] = rowid
        
        sql = """
        SELECT * FROM PEOPLE
        WHERE PEOPLE_ID=%s
        """
        params = (rowid,)
        return apis["PEOPLE"].view_call(sql, params, meta)
    
    @haxdb.app.route("/PEOPLE/save", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_save(rowid=None,col=None,val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        
        meta = {}
        meta["api"] = "PEOPLE"
        meta["action"] = "save"
        meta["rowid"] = rowid
        meta["col"] = col
        meta["val"] = val
        meta["oid"] = "PEOPLE-%s-%s" % (rowid,col)
        
        sql = "UPDATE PEOPLE SET {}=%s WHERE PEOPLE_ID=%s"
        params = (val, rowid)
        return apis["PEOPLE"].save_call(sql, params, meta, col, val, rowid)

    
    @haxdb.app.route("/PEOPLE/new", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/new/<email>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_new(email=None):
        email = email or haxdb.data.var.get("email")

        
        meta = {}
        meta["api"] = "PEOPLE"
        meta["action"] = "new"
        meta["email"] = email

        if not email:
            return haxdb.data.output(success=0, message="MISSING INPUT: email", meta=meta)

        sql = "INSERT INTO PEOPLE (PEOPLE_EMAIL,PEOPLE_DBA) VALUES (%s,0)"
        db.query(sql,(email,))

        if db.rowcount > 0:
            meta["rowid"] = db.lastrowid
            db.commit()
            return haxdb.data.output(success=1, meta=meta)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", meta=meta)
    
    @haxdb.app.route("/PEOPLE/delete/", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_people_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        
        meta = {}
        meta["api"] = "PEOPLE"
        meta["action"] = "delete"
        meta["rowid"] = rowid
        
        if not rowid:
            return haxdb.data.output(success=0, message="MISSING INPUT: rowid", meta=meta)
        
        sql = "DELETE FROM PEOPLE WHERE PEOPLE_ID = %s"
        db.query(sql,(rowid,))

        if db.rowcount > 0:
            db.commit();
            return haxdb.data.output(success=1, meta=meta)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", meta=meta)
    
    
