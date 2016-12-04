db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table('ASSETS_RFID')
    t.add("ASSETS_RFID_ASSETS_ID", "INT", col_required=True, fk_table="ASSETS", fk_col="ASSETS_ID")
    t.add("ASSETS_RFID_AUTO_LOG", "INT", col_size=1)
    t.add("ASSETS_RFID_REQUIRE_RFID", "INT", col_size=1)
    t.add("ASSETS_RFID_REQUIRE_AUTH", "INT", col_size=1)
    t.add("ASSETS_RFID_AUTH_TIMEOUT", "INT")
    t.add("ASSETS_RFID_AUTH_PEOPLE_ID", "INT", fk_table="PEOPLE", fk_col="PEOPLE_ID")
    t.add("ASSETS_RFID_AUTH_START", "INT")
    t.add("ASSETS_RFID_AUTH_LAST", "INT")
    t.add("ASSETS_RFID_STATUS", "CHAR")
    t.add("ASSETS_RFID_STATUS_DESC", "CHAR")
    tables.append(t)
    
    t = db.tables.table('PEOPLE_RFID')
    t.add("PEOPLE_RFID_NAME", "CHAR", col_size=50)
    t.add("PEOPLE_RFID_PEOPLE_ID", "INT", col_required=True, fk_table="PEOPLE", fk_col="PEOPLE_ID")
    t.add("PEOPLE_RFID_RFID", "ASCII", col_size=255)
    t.add("PEOPLE_RFID_ENABLED", "INT", col_size=1)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("ASSETS_RFID", ["ASSETS_RFID_ASSETS_ID"], unique=True))
    indexes.append(db.tables.index("ASSETS_RFID", ["ASSETS_RFID_AUTH_PEOPLE_ID"]))
    indexes.append(db.tables.index("PEOPLE_RFID", ["PEOPLE_RFID_PEOPLE_ID","PEOPLE_RFID_RFID"], unique=True))
    
    db.create(tables=tables, indexes=indexes)    
    
def run():
    
    sql = "SELECT * FROM LISTS WHERE LISTS_NAME = 'LOG ACTIONS'"
    db.query(sql)
    row = db.next()
    lists_id = row["LISTS_ID"]
    
    sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER, LIST_ITEMS_INTERNAL) VALUES (%s, %s, %s, 1, 99, 1)"
    log_actions = ["RFID AUTH","RFID DENY","RFID REGISTER","RFID DEAUTH"]
    for log_action in log_actions:
        db.query(sql, (lists_id, log_action, log_action,), squelch=True)
        db.commit()

    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (%s,1)"
    db.query(sql, ("ASSET STATUSES",), squelch=True)
    db.commit()        
    
    sql = "SELECT * FROM LISTS WHERE LISTS_NAME = 'ASSET STATUSES'"
    db.query(sql)
    row = db.next()
    lists_id = row["LISTS_ID"]
    asset_statuses = ["OPERATIONAL","BORKEN"]
    sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER, LIST_ITEMS_INTERNAL) VALUES (%s, %s, %s, 1, 99, 1)"
    for asset_status in asset_statuses:
        db.query(sql, (lists_id, asset_status, asset_status,), squelch=True)
        db.commit()
    