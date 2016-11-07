db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    t = db.tables.table('RFID_ASSET')
    t.add("RFID_ASSET_ASSETS_ID", "INT", col_required=True, fk_table="ASSETS", fk_col="ASSETS_ID")
    t.add("RFID_ASSET_AUTO_LOG", "INT", col_size=1)
    t.add("RFID_ASSET_REQUIRE_AUTH", "INT", col_size=1)
    t.add("RFID_ASSET_IDLE_TIMEOUT", "INT")
    t.add("RFID_ASSET_STATUS", "CHAR", col_size=25)
    t.add("RFID_ASSET_STATUS_PEOPLE_ID", "INT", fk_table="PEOPLE", fk_col="PEOPLE_ID")
    t.add("RFID_ASSET_STATUS_START", "INT")
    t.add("RFID_ASSET_STATUS_LAST", "INT")


    t = db.tables.table('RFID_ASSET_AUTHS')
    t.add("RFID_ASSET_AUTHS_ASSETS_ID", "INT", col_required=True)
    t.add("RFID_ASSET_AUTHS_PEOPLE_ID", "INT", col_required=True)
    tables.append(t)
        
    indexes = []
    indexes.append(db.tables.index("RFID_ASSET_AUTHS", ["RFID_ASSET_AUTHS_ASSETS_ID", "RFID_ASSET_AUTHS_PEOPLE_ID"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
def run():
    
    sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL, PEOPLE_COLUMNS_GUI, PEOPLE_COLUMNS_QUICKEDIT) VALUES (?,1,?,?,?,?,1,1,1)"
    
    db.query(sql, ("RFID",50,"TEXT",0,"ACCESS"))
    db.commit()
    
    sql = "SELECT * FROM LISTS WHERE LISTS_NAME = 'LOG ACTIONS'"
    db.query(sql)
    row = db.next()
    lists_id = row["LISTS_ID"]
    
    log_action = "AUTHENTICATE"
    sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) VALUES (?, ?, ?, 1, 99)"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()

    log_action = "DENY"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()

    log_action = "ACTIVATE"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()

    log_action = "REGISTER"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()
    
    log_action = "DEACTIVATE"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()
    
    
    