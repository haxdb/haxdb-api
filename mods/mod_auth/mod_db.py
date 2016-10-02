db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("PEOPLE")
    t.add("PEOPLE_EMAIL", "CHAR", col_size=255, col_required=True)
    t.add("PEOPLE_DBA", "INT", col_size=1, col_required=True)
    t.add("PEOPLE_API_KEY_ID", "INT")
    tables.append(t)
    
    t = db.tables.table("AUTH_TOKEN")
    t.add("AUTH_TOKEN_TOKEN", "CHAR", 255, col_required=True)
    t.add("AUTH_TOKEN_EMAIL", "CHAR", 255, col_required=True)
    t.add("AUTH_TOKEN_EXPIRE", "INT", col_required=True)
    tables.append(t)
    
    t = db.tables.table("API_KEYS")
    t.add("API_KEYS_KEY","CHAR",255, col_required=True)
    t.add("API_KEYS_PEOPLE_ID","INT")
    t.add("API_KEYS_READONLY","INT", col_size=1, col_required=True)
    t.add("API_KEYS_DESCRIPTION","CHAR", col_size=255)
    t.add("API_KEYS_IP","CHAR", col_size=15)
    t.add("API_KEYS_DBA","INT", col_size=1, col_required=True)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("PEOPLE", ["PEOPLE_EMAIL"], unique=True))
    indexes.append(db.tables.index("AUTH_TOKEN", ["AUTH_TOKEN_TOKEN"], unique=True))
    indexes.append(db.tables.index("API_KEYS", ["API_KEYS_KEY"], unique=True))
    
    db.create(tables=tables, indexes=indexes)
    

def run():
    pass
