db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("PEOPLE")
    t.add("PEOPLE_NAME_FIRST", "CHAR", col_size=50)
    t.add("PEOPLE_NAME_LAST", "CHAR", col_size=50)
    t.add("PEOPLE_EMAIL", "CHAR", col_size=255)
    t.add("PEOPLE_DBA", "INT", col_size=1, col_required=True)
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("PEOPLE", ["PEOPLE_EMAIL"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    
def run():
    
    
    """
    find_sql = "select LISTS_ID FROM LISTS WHERE LISTS_NAME=?"
    insert_sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL, PEOPLE_COLUMNS_LISTS_ID, PEOPLE_COLUMNS_GUI, PEOPLE_COLUMNS_QUICKEDIT) VALUES (?,1,?,?,?,?,?,?,1,1)"
        
    db.query(find_sql, ("MEMBERSHIP TYPES",))
    row = db.next()
    if row:
        db.query(insert_sql, ("MEMBERSHIP",4,"LIST",1,"PRIMARY",1, row["LISTS_ID"]), squelch=True)
        db.commit()
"""    