db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    
    t = db.tables.table("NODES")
    t.add("NODES_API_KEY","CHAR", col_size=255, col_required=True)
    t.add("NODES_PEOPLE_ID","INT")
    t.add("NODES_ASSETS_ID","INT")
    t.add("NODES_NAME","CHAR", col_size=25)
    t.add("NODES_DESCRIPTION","CHAR", col_size=255)
    t.add("NODES_READONLY","INT", col_size=1, col_required=True)
    t.add("NODES_DBA","INT", col_size=1, col_required=True)
    t.add("NODES_IP","CHAR", col_size=15)
    t.add("NODES_ENABLED","INT", col_size=1, col_required=True)
    t.add("NODES_STATUS", "INT", col_size=1, col_required=True) # 0=REGISTERED, 1=ACCEPTED, -1=DECLINED
    tables.append(t)

    
    indexes = []
    indexes.append(db.tables.index("NODES", ["NODES_API_KEY"], unique=True))
    indexes.append(db.tables.index("NODES", ["NODES_STATUS"]))
    
    db.create(tables=tables, indexes=indexes)
    

def run():
    pass
