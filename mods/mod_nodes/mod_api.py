import os, base64, json, time
from flask import request

api = None
db = None
config = None
tools = None

def init(app_api, app_db, app_config, mod_tools):
    global api, db, config, tools
    api = app_api
    db = app_db
    config = app_config
    tools = mod_tools


def run():
    global api, config, db, tools

    @api.app.before_request
    def mod_api_keys_before_request():
        api.sess.permanent = True
        key = api.data.get("api_key", use_session=True)
        
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
                api.session.set("api_authenticated", 1)
                api.session.set("api_people_id",row["NODES_PEOPLE_ID"])
                api.session.set("nodes_id",row["NODES_ID"])
                api.session.set("api_key",row["NODES_API_KEY"])
                api.session.set("api_readonly",row["NODES_READONLY"])
                api.session.set("api_dba",row["NODES_DBA"])
            else:
                api.session.set("api_authenticated", 0)
        
  
    @api.app.route("/NODES/list", methods=["POST","GET"])
    @api.require_auth
    @api.require_dba
    def mod_api_keys_list():
        people_id = api.data.get("people_id")
        assets_id = api.data.get("assets_id")
        query = api.data.get("query")
        status = api.data.get("status") or '1'
        dba = api.data.get("dba")
        readonly = api.data.get("readonly")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["people_id"] = people_id
        data["input"]["assets_id"] = assets_id
        data["input"]["status"] = status
        data["input"]["dba"] = dba
        data["input"]["readonly"] = readonly
        
        
        sql = """
        SELECT PEOPLE_EMAIL, ASSETS_NAME, NODES.*
        FROM NODES
        LEFT OUTER JOIN PEOPLE ON NODES_PEOPLE_ID=PEOPLE_ID
        LEFT OUTER JOIN ASSETS ON NODES_ASSETS_ID=ASSETS_ID
        WHERE
        NODES_STATUS = ?
        """
        params = (status,)
        
        if query: 
            query = "%" + query + "%"
            sql += """
            AND (
            PEOPLE_EMAIL LIKE ?
            OR NODES_API_KEY LIKE ?
            OR NODES_IP LIKE ?
            OR NODES_NAME LIKE ?
            OR NODES_DESCRIPTION LIKE ?
            )
            """
            params += (query, query, query, query, query,)
            
        if dba:
            sql += " AND NODES_DBA=?"
            params += (dba,)
            
        if readonly:
            sql += " AND NODES_READONLY=?"
            params += (readonly,)
            
        if people_id:
            sql += " AND NODES_PEOPLE_ID=?"
            params += (people_id, )
            
        if assets_id:
            sql += " AND NODES_ASSETS_ID=?"
            params += (assets_id, )
                
        db.query(sql,params)
        rows = []
        row = db.next()
        while row:
            rows.append(dict(row))
            row = db.next()

        return api.output(success=1, rows=rows, data=data)

    @api.app.route("/NODES/new", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_nodes_create():
        is_dba = (api.session.get("api_dba") == 1)
        people_id = api.data.get("people_id") or api.session.get("api_people_id")
        dba = api.data.get("dba") or '0'
        readonly = api.data.get("readonly") or '0'
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "new"
        data["input"]["people_id"] = people_id
        data["input"]["dba"] = dba
        data["input"]["readonly"] = readonly

        if not is_dba:
            people_id = api.session.get("api_people_id")
            dba = 0

        api_key = tools.create_api_key()
        
        sql = """
        INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_READONLY, NODES_DBA, NODES_ENABLED, NODES_STATUS)
        VALUES (?,?,?,?,'0','1')
        """
        db.query(sql, (api_key,people_id,readonly,dba,))

        if db.error:
            return api.output(success=0, data=data, message=db.error)

        if db.rowcount > 0:
            data["rowid"] = db.lastrowid
            sql = "SELECT * FROM NODES WHERE NODES_ID=?"
            db.query(sql, (data["rowid"],))
            if db.error:
                return api.output(success=0, data=data, message=db.error)
            data["row"] = dict(db.next())
            db.commit()
            return api.output(success=1, data=data)

        return api.output(success=0, data=data, message="UNKNOWN ERROR")
        
  
        
    
    @api.app.route("/NODES/save", methods=["GET","POST"])
    @api.app.route("/NODES/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_nodes_save (rowid=None, col=None, val=None):
        valid_cols = ["NODES_DBA","NODES_READONLY","NODES_NAME","NODES_DESCRIPTION","NODES_IP","NODES_ENABLED","NODES_ASSETS_ID"]
        limited_cols = ["NODES_DBA","NODES_READONLY","NODES_IP","NODES_NAME","NODES_ENABLED","NODES_ASSETS_ID"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")
        
        dba = (api.session.get("api_dba") == 1)
        people_id = api.session.get("api_people_id")
        key_id = api.session.get("nodes_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "NODES-%s-%s" % (rowid,col,)
        
        if col not in valid_cols:
            return api.output(success=0, message="INVALID VALUE: col", data=data)

        if col in limited_cols and int(key_id) == int(rowid):
            return api.output(success=0, message="CANNOT UPDATE KEY YOU ARE CURRENTLY USING", data=data)
        
        if col in ("NODES_DBA","NODES_READONLY") and val not in ("0","1"):
            return api.output(success=0, message="INVALID VALUE: val", data=data)

        if col == "NODES_DBA" and not dba:
            return api.output(success=0, message="INVALID PERMISSION", data=data)
        
        if dba:
            sql = "UPDATE NODES SET %s=? WHERE NODES_ID=?" % (col,)
            db.query(sql,(val, rowid))
        else:
            sql = "UPDATE NODES SET %s=? WHERE NODES_ID=? and NODES_PEOPLE_ID=?" % (col,)
            db.query(sql,(val, rowid, people_id,))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, message="SAVED", data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID PERMISSION", data=data)
        
    
    @api.app.route("/NODES/delete", methods=["GET","POST"])
    @api.app.route("/NODES/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_nodes_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")
        
        dba = (api.session.get("api_dba") == 1)
        people_id = api.session.get("api_people_id")
        key_id = api.session.get("nodes_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "NODES"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        
        if key_id == rowid:
            return api.output(success=0, message="CANNOT DELETE KEY YOU ARE CURRENTLY USING", data=data)
        
        if dba:
            sql = "DELETE FROM NODES WHERE NODES_ID=?"
            db.query(sql,(rowid,))
        else:
            sql = "DELETE FROM NODES WHERE NODES_ID=? AND NODES_PEOPLE_ID=?"
            db.query(sql,(rowid, people_id))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, message="DELETED", data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="INVALID PERMISSION", data=data)         
    
    
