import os, base64, json, time

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
    @api.app.route("/LOGS/list", methods=["POST","GET"])
    @api.require_auth
    @api.require_dba
    def mod_logs_list():
        query = api.var.get("query")
    
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LOGS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        
        sql = """
        SELECT LOGS.*, ASSETS.*, 
        NODES_NAME AS LOGS_NODE_NAME,
        ACTION.LIST_ITEMS_VALUE as ACTION_VALUE, ACTION.LIST_ITEMS_DESCRIPTION as ACTION_DESCRIPTION,
        PFN.PEOPLE_COLUMN_VALUES_VALUE as ACTION_FIRST_NAME,
        PLN.PEOPLE_COLUMN_VALUES_VALUE as ACTION_LAST_NAME
        FROM LOGS 
        LEFT OUTER JOIN ASSETS ON ASSETS_ID = LOGS_ASSETS_ID
        LEFT OUTER JOIN LIST_ITEMS ACTION ON ACTION.LIST_ITEMS_ID = LOGS_ACTION_ID AND ACTION.LIST_ITEMS_LISTS_ID = (SELECT LISTS_ID FROM LISTS WHERE LISTS_NAME='LOG ACTIONS')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PFN ON PFN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = LOGS_ACTION_PEOPLE_ID AND PFN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PLN ON PLN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = LOGS_ACTION_PEOPLE_ID AND PLN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')
        LEFT OUTER JOIN NODES ON NODES_ID = LOGS_NODES_ID
        """
        if query:
            query = "%" + query + "%"
            sql += "WHERE ASSETS_NAME LIKE ? OR ACTION_VALUE LIKE ? OR ACTION_DESCRIPTION LIKE ? OR ACTION_FIRST_NAME LIKE ? OR ACTION_LAST_NAME LIKE ? OR LOGS_NODE_NAME LIKE ?"
            sql += " ORDER BY LOGS_UPDATED DESC"
            db.query(sql, (query, query, query, query, query, query,))
        else:
            sql += " ORDER BY LOGS_UPDATED DESC"
            db.query(sql)
    
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        data["sql"]=sql
        
        row = db.next()
        rows = []
        while row:
            rows.append(dict(row))
            row = db.next()
    
        return api.output(success=1, rows=rows, data=data)

    @api.app.route("/LOGS/new", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_logs_new():
        assets_id = api.var.get("assets_id")
        assets_name = api.var.get("assets_name")
        actions_id = api.var.get("actions_id")
        actions_name = api.var.get("actions_name")
        people_id = api.var.get("people_id")
        description = api.var.get("description")
        
        log_people_id = api.session.get("api_people_id")
        log_nodes_id = api.session.get("nodes_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LOGS"
        data["input"]["action"] = "new"
        data["input"]["assets_id"] = assets_id
        data["input"]["assets_name"] = assets_name
        data["input"]["actions_id"] = actions_id
        data["input"]["actions_name"] = actions_name
        data["input"]["people_id"] = people_id
        data["input"]["description"] = description
        
        if assets_name and not assets_id:
            sql = "SELECT * FROM ASSETS WHERE ASSET_NAME = ?"
            db.query(sql, (assets_name,))
            row = db.next()
            if not row or not row["ASSETS_ID"]:
                return api.output(success=0, data=data, message="INVALID VALUE: assets_name")
            assets_id = row["ASSETS_ID"]
            
        if actions_name and not actions_id:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG ACTIONS' and LIST_ITEMS_VALUE=?"
            db.query(sql, (actions_name,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return api.output(success=0, data=data, message="INVALID VALUE: actions_name")
            actionid = row["LIST_ITEMS_ID"]

        sql = "INSERT INTO LOGS (LOGS_ASSETS_ID, LOGS_ACTION_ID, LOGS_ACTION_PEOPLE_ID, LOGS_DESCRIPTION, LOGS_LOG_PEOPLE_ID, LOGS_NODES_ID) "
        sql += "VALUES (?, ?, ?, ?, ?, ?)"
        db.query(sql, (assets_id, actions_id, people_id, description, log_people_id, log_nodes_id,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)