import mod_data
import os, base64, json, time
from flask import request, session

haxdb = None
db = None
config = None
tools = None
apis = {}

def init(app_haxdb, app_db, app_config, mod_tools):
    global haxdb, db, config, tools
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = mod_tools
    
    for api_name in mod_data.apis:
        apis[api_name] = haxdb.api.api_call()
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]    


def run():
    global haxdb, db, config, tools

    @haxdb.app.before_request
    def mod_api_keys_before_request():
        session.permanent = True
        key = haxdb.data.var.get("api_key", use_session=True)
        
        if key:
            ip = str(request.environ['REMOTE_ADDR'])
            sql = """
            select * 
            from NODES 
            where 
            NODES_API_KEY=? 
            and NODES_ENABLED='1'
            and (NODES_IP IS NULL OR NODES_IP='' OR NODES_IP=?)
            """
            db.query(sql,(key,ip))
            row = db.next()
            if row and row["NODES_API_KEY"] == key:
                haxdb.data.session.set("api_authenticated", 1)
                haxdb.data.session.set("api_people_id",row["NODES_PEOPLE_ID"])
                haxdb.data.session.set("nodes_id",row["NODES_ID"])
                haxdb.data.session.set("api_key",row["NODES_API_KEY"])
                haxdb.data.session.set("api_readonly",row["NODES_READONLY"])
                haxdb.data.session.set("api_dba",row["NODES_DBA"])
            else:
                haxdb.data.session.set("api_authenticated", 0)
        
  
    @haxdb.app.route("/NODES/list", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_api_keys_list():
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "list"
        
        sql = """
        SELECT 
        NODES.*,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST
        ASSETS_NAME
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        """
        params = ()

        return apis["NODES"].list_call(sql, params, data)

    @haxdb.app.route("/NODES/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_create():
        is_dba = (haxdb.session.get("api_dba") == 1)
        people_id = haxdb.data.var.get("people_id") or haxdb.session.get("api_people_id")
        dba = haxdb.data.var.get("dba") or '0'
        readonly = haxdb.data.var.get("readonly") or '0'
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "new"
        data["input"]["people_id"] = people_id
        data["input"]["dba"] = dba
        data["input"]["readonly"] = readonly

        if not is_dba:
            people_id = haxdb.session.get("api_people_id")
            dba = 0

        api_key = tools.create_api_key()
        
        sql = """
        INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_STATUS)
        VALUES (?,?,?,?,'0','1')
        """
        db.query(sql, (api_key,people_id,readonly,dba,))

        if db.error:
            return haxdb.data.output(success=0, data=data, message=db.error)

        if db.rowcount > 0:
            data["rowid"] = db.lastrowid
            sql = "SELECT * FROM NODES WHERE NODES_ID=?"
            db.query(sql, (data["rowid"],))
            if db.error:
                return haxdb.data.output(success=0, data=data, message=db.error)
            data["row"] = dict(db.next())
            db.commit()
            return haxdb.data.output(success=1, data=data)

        return haxdb.data.output(success=0, data=data, message="UNKNOWN ERROR")
        
  
        
    
    @haxdb.app.route("/NODES/save", methods=["GET","POST"])
    @haxdb.app.route("/NODES/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_save (rowid=None, col=None, val=None):
        valid_cols = ["NODES_DBA","NODES_READONLY","NODES_NAME","NODES_DESCRIPTION","NODES_IP","NODES_ENABLED","NODES_ASSETS_ID","NODES_STATUS"]
        limited_cols = ["NODES_DBA","NODES_READONLY","NODES_IP","NODES_NAME","NODES_ENABLED","NODES_ASSETS_ID","NODES_STATUS"]
        
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        dba = (haxdb.data.session.get("api_dba") == 1)
        people_id = haxdb.data.session.get("api_people_id")
        key_id = haxdb.data.session.get("nodes_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "NODES-%s-%s" % (rowid,col,)
        
        if col not in valid_cols:
            return haxdb.data.output(success=0, message="INVALID VALUE: col", data=data)

        if col in limited_cols and int(key_id) == int(rowid):
            return haxdb.data.output(success=0, message="CANNOT UPDATE KEY YOU ARE CURRENTLY USING", data=data)
        
        if col in ("NODES_DBA","NODES_READONLY") and val not in ("0","1"):
            return haxdb.data.output(success=0, message="INVALID VALUE: val", data=data)

        if col == "NODES_DBA" and not dba:
            return haxdb.data.output(success=0, message="INVALID PERMISSION", data=data)
        
        if dba:
            sql = "UPDATE NODES SET %s=? WHERE NODES_ID=?" % (col,)
            db.query(sql,(val, rowid))
        else:
            sql = "UPDATE NODES SET %s=? WHERE NODES_ID=? and NODES_PEOPLE_ID=?" % (col,)
            db.query(sql,(val, rowid, people_id,))
 
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, message="SAVED", data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="INVALID PERMISSION", data=data)
        
    
    @haxdb.app.route("/NODES/delete", methods=["GET","POST"])
    @haxdb.app.route("/NODES/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        
        dba = (haxdb.session.get("api_dba") == 1)
        people_id = haxdb.session.get("api_people_id")
        key_id = haxdb.session.get("nodes_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        
        if key_id == rowid:
            return haxdb.data.output(success=0, message="CANNOT DELETE KEY YOU ARE CURRENTLY USING", data=data)
        
        if dba:
            sql = "DELETE FROM NODES WHERE NODES_ID=?"
            db.query(sql,(rowid,))
        else:
            sql = "DELETE FROM NODES WHERE NODES_ID=? AND NODES_PEOPLE_ID=?"
            db.query(sql,(rowid, people_id))
 
        if db.rowcount > 0:
            db.commit()
            return haxdb.data.output(success=1, message="DELETED", data=data)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, data=data)
        
        return haxdb.data.output(success=0, message="INVALID PERMISSION", data=data)         
    
    
