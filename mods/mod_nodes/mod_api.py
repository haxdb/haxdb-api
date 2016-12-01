import mod_data
import os, base64, json, time, datetime
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
        def calc_row(row):
            row["NODES_EXPIRE_VIEW"] = "N/A"
            try:
                row["NODES_EXPIRE_VIEW"] = datetime.datetime.fromtimestamp(row["NODES_EXPIRE"]).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
            return row
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "list"
        
        sql = "DELETE FROM NODES WHERE NODES_EXPIRE<?"
        db.query(sql,(time.time(),))
        
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

        return apis["NODES"].list_call(sql, params, data, calc_row)

    @haxdb.app.route("/NODES/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_create():
        is_dba = (haxdb.session.get("api_dba") == 1)
        people_id = haxdb.data.var.get("people_id") or haxdb.session.get("api_people_id")
        dba = haxdb.data.var.get("dba") or '0'
        readonly = haxdb.data.var.get("readonly") or '0'
        expire_seconds = haxdb.data.var.get("expire_seconds") 
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "new"
        data["input"]["people_id"] = people_id
        data["input"]["dba"] = dba
        data["input"]["readonly"] = readonly
        data["input"]["expire_seconds"] = expire_seconds

        if not is_dba:
            people_id = haxdb.session.get("api_people_id")
            dba = 0

        api_key = tools.create_api_key()
        
        if expire_seconds:
            expire_time = int(time.time()) + int(expire_seconds)
            sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_QUEUED, NODES_EXPIRE)
                    VALUES (?,?,?,?,'0','0',?)
                    """
            params = (api_key,people_id,readonly,dba,expire_time)
        else:
            sql = """
                    INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_QUEUED)
                    VALUES (?,?,?,?,'0','0')
                    """
            params = (api_key,people_id,readonly,dba,)

        return apis["NODES"].new_call(sql, params, data)
        
  
        
    
    @haxdb.app.route("/NODES/save", methods=["GET","POST"])
    @haxdb.app.route("/NODES/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        key_id = haxdb.data.session.get("nodes_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "NODES-%s-%s" % (rowid,col,)
        
        if int(key_id) == int(rowid):
            return haxdb.data.output(success=0, message="CANNOT UPDATE KEY YOU ARE CURRENTLY USING", data=data)
        
        sql = "UPDATE NODES SET %s=? WHERE NODES_ID=?"
        params = (val, rowid)
        return apis["NODES"].save_call(sql, params, data, col, val, rowid)
    
    @haxdb.app.route("/NODES/delete", methods=["GET","POST"])
    @haxdb.app.route("/NODES/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_nodes_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        key_id = haxdb.session.get("nodes_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        if int(key_id) == int(rowid):
            return haxdb.data.output(success=0, message="CANNOT DELETE KEY YOU ARE CURRENTLY USING", data=data)
        
        sql = "DELETE FROM NODES WHERE NODES_ID=?"
        params = (rowid,)
 
        return apis["NODES"].delete_call(sql, params, data)