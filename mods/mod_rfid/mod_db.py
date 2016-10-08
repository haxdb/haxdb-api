db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    
    
def run():
    
    sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL) VALUES (?,1,?,?,?,?,?)"
    
    db.query(sql, ("RFID",50,"TEXT",0,"ACCESS",1))
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
    
    log_action = "DEACTIVATE"
    db.query(sql, (lists_id, log_action, log_action,))
    db.commit()
    
    
    