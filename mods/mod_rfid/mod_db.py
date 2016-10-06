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
    
    