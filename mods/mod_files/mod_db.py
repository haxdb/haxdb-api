db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table("FILES")
    t.add("FILES_CONTEXT", "CHAR", col_size=50)
    t.add("FILES_CONTEXT_ID", "INT")
    t.add("FILES_ROWID", "INT")
    t.add("FILES_EXT", "CHAR", col_size=5)
    t.add("FILES_MIMETYPE", "CHAR", col_size=50)
    t.add("FILES_DATA", "BLOB")
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("FILES", ["FILES_CONTEXT",
                                             "FILES_CONTEXT_ID",
                                             "FILES_ROWID"], unique=True))

    db.create(tables=tables, indexes=indexes)


def run():
    pass
