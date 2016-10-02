db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("LISTS")
    t.add("LISTS_NAME", "CHAR", col_size=50, col_required=True)
    t.add("LISTS_INTERNAL", "INT", col_size=1)
    tables.append(t)
    
    t = db.tables.table('LIST_ITEMS')
    t.add("LIST_ITEMS_LISTS_ID", "INT", col_required=True)
    t.add("LIST_ITEMS_VALUE", "CHAR", col_size=255, col_required=True)
    t.add("LIST_ITEMS_DESCRIPTION", "CHAR", col_size=255, col_required=True)
    t.add("LIST_ITEMS_ENABLED", "INT", col_size=1, col_required=True)
    t.add("LIST_ITEMS_ORDER", "INT", col_required=True)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("LISTS", ["LISTS_NAME"], unique=True))
    indexes.append(db.tables.index("LIST_ITEMS", ["LIST_ITEMS_LISTS_ID","LIST_ITEMS_VALUE"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (?,1)"
    db.query(sql, ("MEMBERSHIP TYPES",))
    db.query(sql, ("YES/NO",))
    db.query(sql, ("TRUE/FALSE",))
    db.commit()

    
def run():

    find_sql = "select LISTS_ID FROM LISTS WHERE LISTS_NAME=?"

    db.query(find_sql, ("YES/NO",))
    row = db.next()
    options_sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) VALUES (%s, ?, ?, 1, ?)" % row["LISTS_ID"]
    db.query(options_sql, ( "1", "YES", 1 ) )  
    db.query(options_sql, ( "0", "NO", 2 ) )  
    db.commit()

    db.query(find_sql, ("TRUE/FALSE",))
    row = db.next()
    options_sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) VALUES (%s, ?, ?, 1, ?)" % row["LISTS_ID"]
    db.query(options_sql, ( "1", "TRUE", 1 ) )  
    db.query(options_sql, ( "0", "FALSE", 2 ) )      
    db.commit()

    db.query(find_sql, ("MEMBERSHIP TYPES",))
    row = db.next()
    options_sql = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_ORDER) VALUES (%s, ?, ?, 1, ?)" % row["LISTS_ID"]
    db.query(options_sql, ( "NONE", "NONE", 1 ) )  
    db.query(options_sql, ( "TRIAL", "TRIAL", 2 ) )      
    db.query(options_sql, ( "MEMBER", "MEMBER", 3 ) )      
    db.commit()
    
