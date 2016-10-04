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
        assetid = api.data.get("assetid")
        asset = api.data.get("asset")
        actionid = api.data.get("actionid")
        action = api.data.get("action")
        peopleid = api.data.get("peopleid")
        nodeid = api.data.get("nodeid")
        node = api.data.get("node")
        description = api.data.get("description")
        
        log_people_id = api.session.get("api_people_id")
        log_api_key = api.session.get("api.api_key")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "LOGS"
        data["input"]["action"] = "new"
        data["input"]["assetid"] = assetid
        data["input"]["asset"] = asset
        data["input"]["actionid"] = actionid
        data["input"]["action"] = action
        data["input"]["peopleid"] = peopleid
        data["input"]["nodeid"] = nodeid
        data["input"]["node"] = node
        data["input"]["description"] = description
        
        if asset and not assetid:
            sql = "SELECT * FROM ASSETS WHERE ASSET_NAME = ?"
            db.query(sql, (asset,))
            row = db.next()
            if not row or not row["ASSETS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: asset")
            assetid = row["ASSETS_ID"]
            
        if action and not actionid:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG ACTIONS' and LIST_ITEMS_VALUE=?"
            db.query(sql, (action,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: action")
            actionid = row["LIST_ITEMS_ID"]

        if node and not nodeid:
            sql = "SELECT * FROM LISTS JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID WHERE LISTS_NAME='LOG NODES' and LIST_ITEMS_VALUE=?"
            db.query(sql, (node,))
            row = db.next()
            if not row or not row["LIST_ITEMS_ID"]:
                return api.output(success=0, data=data, info="INVALID VALUE: node")
            nodeid = row["LIST_ITEMS_ID"]
            
        sql = "INSERT INTO LOGS (LOGS_ASSETS_ID, LOGS_ACTION_ID, LOGS_ACTION_PEOPLE_ID, LOGS_NODE_ID, LOGS_DESCRIPTION, LOGS_LOG_PEOPLE_ID, LOGS_API_KEY_ID) "
        sql += "VALUES (?, ?, ?, ?, ?, ?, ?)"
        db.query(sql, (assetid, actionid, peopleid, nodeid, description, log_people_id, log_api_key,))
        if db.rowcount > 0:
            db.commit()
            data["rowid"] = db.lastrowid
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="UNKNOWN ERROR", data=data)