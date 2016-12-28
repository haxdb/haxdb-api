db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table("UDF")
    t.add("UDF_CONTEXT", "CHAR", col_size=50, col_required=True)
    t.add("UDF_CONTEXT_ID", "INT")
    t.add("UDF_CATEGORY", "CHAR", col_size=50)
    t.add("UDF_NAME", "CHAR", col_size=50, col_required=True)
    t.add("UDF_TYPE", "CHAR", col_size=50)
    t.add("UDF_LISTS_ID", "INT")
    t.add("UDF_ORDER", "FLOAT")
    t.add("UDF_ENABLED", "INT", col_size=1)
    t.add("UDF_KEY", "INT", col_size=1)
    t.add("UDF_INTERNAL", "INT", col_size=1)
    tables.append(t)

    t = db.tables.table('UDF_DATA')
    t.add("UDF_DATA_UDF_ID", "INT", col_required=True, fk_table="UDF", fk_col="UDF_ID")
    t.add("UDF_DATA_ROWID", "INT", col_required=True)
    t.add("UDF_DATA_VALUE", "CHAR", col_size=255)
    tables.append(t)

    """
    t = db.tables.table('UDF_BLOB')
    t.add("UDF_BLOB_UDF_DATA_ID", "INT", col_required=True)
    t.add("UDF_BLOB_MIME_TYPE", "CHAR", col_size=255)
    t.add("UDF_BLOB_VALUE", "BLOB")
    tables.append(t)
    """

    indexes = []
    indexes.append(db.tables.index("UDF", ["UDF_CONTEXT", "UDF_CONTEXT_ID", "UDF_NAME"], unique=True))
    indexes.append(db.tables.index("UDF_DATA", ["UDF_DATA_UDF_ID", "UDF_DATA_ROWID"], unique=True))
    #indexes.append(db.tables.index("UDF_BLOB", ["UDF_BLOB_UDF_DATA_ID"], unique=True))

    db.create(tables=tables, indexes=indexes)


def run():
    pass
