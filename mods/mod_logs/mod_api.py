import os, base64, json, time

haxdb = None
db = None
config = None
tools = None

def init(app_haxdb, app_db, app_config, mod_tools):
    global haxdb, db, config, tools
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = mod_tools


def run():
    @haxdb.app.route("/LOGS/list", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_logs_list():
        query = haxdb.data.var.get("query")
    
        
        meta = {}
        meta["api"] = "LOGS"
        meta["action"] = "list"
        meta["query"] = query
        
        sql = """
        SELECT LOGS.*, ASSETS.*, 
        NODES_NAME AS LOGS_NODE_NAME,
        ACTION.LIST_ITEMS_VALUE as ACTION_VALUE, ACTION.LIST_ITEMS_DESCRIPTION as ACTION_DESCRIPTION,
        PEOPLE_NAME_LAST, PEOPLE_NAME_FIRST
        FROM LOGS 
        LEFT OUTER JOIN ASSETS ON ASSETS_ID = LOGS_ASSETS_ID
        LEFT OUTER JOIN LIST_ITEMS ACTION ON ACTION.LIST_ITEMS_ID = LOGS_ACTION_ID AND ACTION.LIST_ITEMS_LISTS_ID = (SELECT LISTS_ID FROM LISTS WHERE LISTS_NAME='LOG ACTIONS')
        LEFT OUTER JOIN PEOPLE ON PEOPLE_ID=LOGS_ACTION_PEOPLE_ID
        LEFT OUTER JOIN NODES ON NODES_ID = LOGS_NODES_ID
        """
        if query:
            query = "%" + query + "%"
            sql += "WHERE ASSETS_NAME LIKE %s OR ACTION_VALUE LIKE %s OR ACTION_DESCRIPTION LIKE %s OR ACTION_FIRST_NAME LIKE %s OR ACTION_LAST_NAME LIKE %s OR LOGS_NODE_NAME LIKE %s"
            sql += " ORDER BY LOGS_UPDATED DESC"
            db.query(sql, (query, query, query, query, query, query,))
        else:
            sql += " ORDER BY LOGS_UPDATED DESC"
            db.query(sql)
    
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return haxdb.data.output(success=1, rows=rows, meta=meta)

    @haxdb.app.route("/LOGS/new", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_logs_new():
        assets_id = haxdb.data.var.get("assets_id")
        assets_name = haxdb.data.var.get("assets_name")
        actions_id = haxdb.data.var.get("actions_id")
        actions_name = haxdb.data.var.get("actions_name")
        people_id = haxdb.data.var.get("people_id")
        description = haxdb.data.var.get("description")
        
        log_people_id = haxdb.session.get("api_people_id")
        log_nodes_id = haxdb.session.get("nodes_id")
        
        
        meta = {}
        meta["api"] = "LOGS"
        meta["action"] = "new"
        meta["assets_id"] = assets_id
        meta["assets_name"] = assets_name
        meta["actions_id"] = actions_id
        meta["actions_name"] = actions_name
        meta["people_id"] = people_id
        meta["description"] = description
        
        if assets_name and not assets_id:
            sql = "SELECT * FROM ASSETS WHERE ASSET_NAME = %s"
            db.query(sql, (assets_name,))
            row = db.next()
            if not row or not row["ASSETS_ID"]:
                return haxdb.data.output(success=0, meta=meta, message="INVALID VALUE: assets_name")
            assets_id = row["ASSETS_ID"]
            
        if actions_name and not actions_id:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG ACTIONS' and LIST_ITEMS_VALUE=%s"
            db.query(sql, (actions_name,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return haxdb.data.output(success=0, meta=meta, message="INVALID VALUE: actions_name")
            actionid = row["LIST_ITEMS_ID"]

        sql = "INSERT INTO LOGS (LOGS_ASSETS_ID, LOGS_ACTION_ID, LOGS_ACTION_PEOPLE_ID, LOGS_DESCRIPTION, LOGS_LOG_PEOPLE_ID, LOGS_NODES_ID) "
        sql += "VALUES (%s, %s, %s, %s, %s, %s)"
        db.query(sql, (assets_id, actions_id, people_id, description, log_people_id, log_nodes_id,))
        if db.rowcount > 0:
            db.commit()
            meta["rowid"] = db.lastrowid
            return haxdb.data.output(success=1, meta=meta)
        
        if db.error:
            return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        return haxdb.data.output(success=0, message="UNKNOWN ERROR", meta=meta)