db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("FIELDSET")
    t.add("FIELDSET_NAME", "CHAR", col_size=50)
    t.add("FIELDSET_CONTEXT", "CHAR", col_size=50)
    t.add("FIELDSET_CONTEXT_ID", "INT")
    t.add("FIELDSET_QUERY", "CHAR", col_size=255)
    tables.append(t)

    t = db.tables.table("FIELDSET_COLS")
    t.add("FIELDSET_COLS_FIELDSET_ID", "INT")
    t.add("FIELDSET_COLS_COL", "CHAR", col_size=50)
    t.add("FIELDSET_COLS_ORDER", "CHAR", col_size=255)
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("FIELDSET", ["FIELDSET_NAME"], unique=True))
    indexes.append(db.tables.index("FIELDSET_COLS", ["FIELDSET_COLS_FIELDSET_ID","FIELDSET_COLS_COL"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    
def run():

    insert_list = "INSERT INTO LISTS (LISTS_NAME, LISTS_INTERNAL) VALUES (%s, 1)"
    insert_list_item = "INSERT INTO LIST_ITEMS (LIST_ITEMS_LISTS_ID, LIST_ITEMS_VALUE, LIST_ITEMS_DESCRIPTION, LIST_ITEMS_ENABLED, LIST_ITEMS_INTERNAL, LIST_ITEMS_ORDER) VALUES (%s, %s, %s, 1, 1, 999)"
    find_list = "select LISTS_ID FROM LISTS WHERE LISTS_NAME=%s"
    insert_udf = "INSERT INTO UDF (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_CATEGORY, UDF_NAME, UDF_TYPE, UDF_LISTS_ID, UDF_ORDER, UDF_ENABLED, UDF_INTERNAL) VALUES ('PEOPLE',0,%s,%s,%s,%s,999,1,1)"

    db.query(insert_list, ("MEMBERSHIPS",), squelch=True)

    row = db.qaf(find_list, ("MEMBERSHIPS",))
    if row:
        db.query(insert_list_item, (row["LISTS_ID"], "TRIAL", "TRIAL",), squelch=True)
        db.query(insert_list_item, (row["LISTS_ID"], "MEMBER", "MEMBER",), squelch=True)
        db.commit()
