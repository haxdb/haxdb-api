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
    t.add("LIST_ITEMS_VALUE", "CHAR", col_size=100, col_required=True)
    t.add("LIST_ITEMS_DESCRIPTION", "CHAR", col_size=255, col_required=True)
    t.add("LIST_ITEMS_ENABLED", "INT", col_size=1, col_required=True)
    t.add("LIST_ITEMS_INTERNAL", "INT", col_size=1)
    t.add("LIST_ITEMS_ORDER", "INT", col_required=True)
    tables.append(t)
    
    indexes = []
    indexes.append(db.tables.index("LISTS", ["LISTS_NAME"], unique=True))
    indexes.append(db.tables.index("LIST_ITEMS", ["LIST_ITEMS_LISTS_ID","LIST_ITEMS_VALUE"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (%s,1)"
    db.query(sql, ("YES/NO",), squelch=True)
    db.commit()

    
def run():
    pass
    
