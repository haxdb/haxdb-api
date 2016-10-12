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
    t.add("PEOPLE_NODES_ID", "INT")
    tables.append(t)

    t = db.tables.table("PEOPLE_COLUMNS")
    t.add("PEOPLE_COLUMNS_NAME", "CHAR", col_size=50, col_required=True)
    t.add("PEOPLE_COLUMNS_ENABLED", "INT", col_size=1, col_required=True)
    t.add("PEOPLE_COLUMNS_ORDER", "INT", col_required=True)
    t.add("PEOPLE_COLUMNS_TYPE", "CHAR", col_size=25, col_required=True)
    t.add("PEOPLE_COLUMNS_LISTS_ID", "INT", fk_table="LISTS", fk_col="LISTS_ID")
    t.add("PEOPLE_COLUMNS_KEY", "INT", col_size=1, col_required=True)
    t.add("PEOPLE_COLUMNS_CATEGORY", "CHAR", col_size=25, col_required=True)
    t.add("PEOPLE_COLUMNS_INTERNAL", "INT", col_size=1)
    tables.append(t)
    
    t = db.tables.table("PEOPLE_COLUMN_VALUES")
    t.add("PEOPLE_COLUMN_VALUES_PEOPLE_ID","INT", col_required=True, fk_table="PEOPLE", fk_col="PEOPLE_ID")
    t.add("PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID","INT", col_required=True, fk_table="PEOPLE_COLUMNS", fk_col="PEOPLE_COLUMNS_ID")
    t.add("PEOPLE_COLUMN_VALUES_VALUE", "CHAR", col_size=255)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("PEOPLE", ["PEOPLE_EMAIL"], unique=True))
    indexes.append(db.tables.index("PEOPLE_COLUMNS", ["PEOPLE_COLUMNS_NAME"], unique=True))
    indexes.append(db.tables.index("PEOPLE_COLUMN_VALUES", ["PEOPLE_COLUMN_VALUES_PEOPLE_ID","PEOPLE_COLUMN_VALUES_PEOPLE_COLUMN_ID"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    
def run():
    
    sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL) VALUES (?,1,?,?,?,?,?)"
    
    db.query(sql, ("FIRST_NAME",1,"TEXT",1,"PRIMARY",1))
    db.query(sql, ("LAST_NAME",2,"TEXT",1,"PRIMARY",1))
    db.query(sql, ("EMAIL",3,"TEXT",1,"PRIMARY",1))
    db.commit()
    
    find_sql = "select LISTS_ID FROM LISTS WHERE LISTS_NAME=?"
    insert_sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL, PEOPLE_COLUMNS_LISTS_ID) VALUES (?,1,?,?,?,?,?,?)"

    db.query(find_sql, ("YES/NO",))
    row = db.next()
    if row:
        db.query(insert_sql, ("DBA",20,"LIST",0,"USER",1, row["LISTS_ID"]))
        db.commit()
        
    db.query(find_sql, ("MEMBERSHIP TYPES",))
    row = db.next()
    if row:
        db.query(insert_sql, ("MEMBERSHIP",4,"LIST",1,"PRIMARY",1, row["LISTS_ID"]))
        db.commit()
    