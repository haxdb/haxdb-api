db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table('THUMBS')
    t.add("THUMBS_TABLE", "CHAR", col_required=True)
    t.add("THUMBS_ROWID", "INT", col_required=True)
    t.add("THUMBS_MIMETYPE", "CHAR", col_required=True)
    t.add("THUMBS_EXT", "CHAR", col_size=5, col_required=True)
    t.add("THUMBS_BIG", "BLOB")
    t.add("THUMBS_SMALL", "BLOB")
    tables.append(t)

    indexes = []
    i = db.tables.index("THUMBS",
                        ["THUMBS_TABLE", "THUMBS_ROWID"],
                        unique=True)
    indexes.append(i)

    db.create(tables=tables, indexes=indexes)


def run():
    pass
