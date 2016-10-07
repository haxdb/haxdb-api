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
        query = api.data.get("query")
    
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LOGS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        
        sql = """
        SELECT LOGS.*, ASSETS.*, 
        ACTION.LIST_ITEMS_VALUE as ACTION_VALUE, ACTION.LIST_ITEMS_DESCRIPTION as ACTION_DESCRIPTION,
        NODE.LIST_ITEMS_VALUE as NODE_VALUE, NODE.LIST_ITEMS_DESCRIPTION as NODE_DESCRIPTION,
        PFN.PEOPLE_COLUMN_VALUES_VALUE as ACTION_FIRST_NAME,
        PLN.PEOPLE_COLUMN_VALUES_VALUE as ACTION_LAST_NAME
        FROM LOGS 
        LEFT OUTER JOIN ASSETS ON ASSETS_ID = LOGS_ASSETS_ID
        LEFT OUTER JOIN LIST_ITEMS ACTION ON ACTION.LIST_ITEMS_ID = LOGS_ACTION_ID AND ACTION.LIST_ITEMS_LISTS_ID = (SELECT LISTS_ID FROM LISTS WHERE LISTS_NAME='LOG ACTIONS')
        LEFT OUTER JOIN LIST_ITEMS NODE ON NODE.LIST_ITEMS_ID = LOGS_NODE_ID AND NODE.LIST_ITEMS_LISTS_ID = (SELECT LISTS_ID FROM LISTS WHERE LISTS_NAME='LOG NODES')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PFN ON PFN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = LOGS_ACTION_PEOPLE_ID AND PFN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PLN ON PLN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = LOGS_ACTION_PEOPLE_ID AND PLN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')
        """
        if query:
            query = "%" + query + "%"
            sql += "ASSETS_NAME LIKE ? OR ACTION_VALUE LIKE ? OR ACTION_DESCRIPTION LIKE ? OR NODE_VALUE LIKE ? OR NODE_DESCRIPTION LIKE ? OR ACTION_FIRST_NAME LIKE ? OR ACTION_LAST_NAME LIKE ?"
            db.query(sql, (query, query, query, query, query, query, query))
        else:
            db.query(sql)
    
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
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
        assets_id = api.data.get("assets_id")
        assets_name = api.data.get("assets_name")
        actions_id = api.data.get("actions_id")
        actions_name = api.data.get("actions_name")
        people_id = api.data.get("people_id")
        nodes_id = api.data.get("nodes_id")
        nodes_name = api.data.get("nodes_name")
        description = api.data.get("description")
        
        log_people_id = api.session.get("api_people_id")
        log_api_key = api.session.get("api.api_key")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LOGS"
        data["input"]["action"] = "new"
        data["input"]["assets_id"] = assets_id
        data["input"]["assets_name"] = assets_name
        data["input"]["actions_id"] = actions_id
        data["input"]["actions_name"] = actions_name
        data["input"]["people_id"] = people_id
        data["input"]["nodes_id"] = nodes_id
        data["input"]["nodes_name"] = nodes_name
        data["input"]["description"] = description
        
        if assets_name and not assets_id:
            sql = "SELECT * FROM ASSETS WHERE ASSET_NAME = ?"
            db.query(sql, (assets_name,))
            row = db.next()
            if not row or not row["ASSETS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: assets_name")
            assets_id = row["ASSETS_ID"]
            
        if actions_name and not actions_id:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG ACTIONS' and LIST_ITEMS_VALUE=?"
            db.query(sql, (actions_name,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: actions_name")
            actionid = row["LIST_ITEMS_ID"]

        if nodes_name and not nodes_id:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG NODES' and LIST_ITEMS_VALUE=?"
            db.query(sql, (nodes_name,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: nodes_name")
            nodeid = row["LIST_ITEMS_ID"]
            
        sql = "INSERT INTO LOGS (LOGS_ASSETS_ID, LOGS_ACTION_ID, LOGS_ACTION_PEOPLE_ID, LOGS_NODE_ID, LOGS_DESCRIPTION, LOGS_LOG_PEOPLE_ID, LOGS_API_KEY_ID) "
        sql += "VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.query(sql, (assets_id, actions_id, people_id, nodes_id, description, log_people_id, log_api_key,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="UNKNOWN ERROR", data=data)