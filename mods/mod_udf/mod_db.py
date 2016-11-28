db = None
config = None

def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config
    
    tables = []
    
    t = db.tables.table("UDF_DEF")
    t.add("UDF_DEF_CONTEXT", "CHAR", col_size=50, col_required=True)
    t.add("UDF_DEF_CONTEXT_ID1", "INT", col_required=True)
    t.add("UDF_DEF_CONTEXT_ID2", "INT")
    t.add("UDF_DEF_CATEGORY", "CHAR", col_size=50)    
    t.add("UDF_DEF_NAME", "CHAR", col_size=50, col_required=True)
    t.add("UDF_DEF_TYPE", "CHAR", col_size=50)
    t.add("UDF_DEF_LISTS_ID", "INT")
    t.add("UDF_DEF_ORDER", "FLOAT")
    t.add("UDF_DEF_ENABLED", "INT", col_size=1)
    t.add("UDF_DEF_KEY", "INT", col_size=1)
    t.add("UDF_DEF_INTERNAL", "INT", col_size=1)
    tables.append(t)
    
    t = db.tables.table('UDF')
    t.add("UDF_UDF_DEF_ID", "INT", col_required=True)
    t.add("UDF_ROWID", "INT", col_required=True)
    t.add("UDF_VALUE", "CHAR", col_size=255)
    tables.append(t)

    t = db.tables.table('UDF_BLOB')
    t.add("UDF_BLOB_UDF_ID", "INT", col_required=True)
    t.add("UDF_BLOB_MIME_TYPE", "CHAR", col_size=255)
    t.add("UDF_BLOB_VALUE", "BLOB")
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("UDF_DEF", ["UDF_DEF_CONTEXT","UDF_DEF_CONTEXT_ID1","UDF_DEF_CONTEXT_ID2","UDF_DEF_NAME"], unique=True))
    indexes.append(db.tables.index("UDF", ["UDF_UDF_DEF_ID","UDF_ROWID"], unique=True))
    indexes.append(db.tables.index("UDF_BLOB", ["UDF_BLOB_UDF_ID"], unique=True))

    db.create(tables=tables, indexes=indexes)    
    
    
def run():
    pass