db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("AUTH_TOKEN")
    t.add("AUTH_TOKEN_TOKEN", "CHAR", 255, col_required=True)
    t.add("AUTH_TOKEN_PEOPLE_ID", "INT", col_required=True)
    t.add("AUTH_TOKEN_EXPIRE", "INT", col_required=True)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("AUTH_TOKEN", ["AUTH_TOKEN_TOKEN"], unique=True))
    indexes.append(db.tables.index("AUTH_TOKEN", ["AUTH_TOKEN_PEOPLE_ID"], unique=True))
    db.create(tables=tables, indexes=indexes)
    

def run():
    pass
