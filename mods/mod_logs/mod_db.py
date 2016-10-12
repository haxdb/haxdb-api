db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("LOGS")
    t.add("LOGS_ASSETS_ID", "INT")
    t.add("LOGS_ACTION_ID", "INT")
    t.add("LOGS_ACTION_PEOPLE_ID", "INT")
    t.add("LOGS_DESCRIPTION", "CHAR", col_size=255, col_required=True)
    t.add("LOGS_LOG_PEOPLE_ID", "INT")
    t.add("LOGS_NODES_ID", "INT")
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("LOGS", ["LOGS_ASSET_ID"]))
    indexes.append(db.tables.index("LOGS", ["LOGS_ACTION_ID"]))
    db.create(tables=tables, indexes=indexes)    
    
    
def run():
    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (?,1)"
    db.query(sql, ("LOG ACTIONS",))

