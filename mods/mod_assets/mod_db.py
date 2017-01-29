db = None
config = None


def init(app_db, app_config):
    global db, config

    db = app_db
    config = app_config

    tables = []

    t = db.tables.table("ASSETS")
    t.add("ASSETS_NAME", "CHAR", col_size=50, col_required=True)
    t.add("ASSETS_TYPE", "CHAR", col_size=50)
    t.add("ASSETS_MANUFACTURER", "CHAR", col_size=50)
    t.add("ASSETS_MODEL", "CHAR", col_size=50)
    t.add("ASSETS_PRODUCT_ID", "CHAR", col_size=50)
    t.add("ASSETS_SERIAL_NUMBER", "CHAR", col_size=50)
    t.add("ASSETS_QUANTITY", "INT")
    t.add("ASSETS_LOCATION", "CHAR")
    t.add("ASSETS_DESCRIPTION", "TEXT")
    t.add("ASSETS_ACQUIRE_DATE", "DATE")
    t.add("ASSETS_ACQUIRE_TYPE", "CHAR")
    t.add("ASSETS_ACQUIRE_PEOPLE_ID", "INT")
    t.add("ASSETS_ACQUIRE_TERMS", "TEXT")
    t.add("ASSETS_RETIRE_DATE", "DATE")
    t.add("ASSETS_RETIRE_TYPE", "CHAR")
    t.add("ASSETS_RETIRE_NOTES", "TEXT")
    t.add("ASSETS_INTERNAL", "INT", col_size=1)
    tables.append(t)

    t = db.tables.table('ASSET_LINKS')
    t.add("ASSET_LINKS_ASSETS_ID", "INT", col_required=True)
    t.add("ASSET_LINKS_NAME", "CHAR", col_size=50, col_required=True)
    t.add("ASSET_LINKS_LINK", "CHAR", col_size=255)
    t.add("ASSET_LINKS_ORDER", "INT")
    tables.append(t)

    """
    t = db.tables.table('ASSET_FILES')
    t.add("ASSET_FILES_ASSETS_ID", "INT", col_required=True)
    t.add("ASSET_FILES_NAME", "CHAR", col_size=50, col_required=True)
    t.add("ASSET_FILES_DATA", "BLOB")
    t.add("ASSET_FILES_ORDER", "INT")
    tables.append(t)

    t = db.tables.table('ASSET_IMAGES')
    t.add("ASSET_FILES_ASSETS_ID", "INT", col_required=True)
    t.add("ASSET_FILES_NAME", "CHAR", col_size=50, col_required=True)
    t.add("ASSET_FILES_DATA", "BLOB")
    t.add("ASSET_FILES_ORDER", "INT")
    tables.append(t)
    """

    t = db.tables.table('ASSET_AUTHS')
    t.add("ASSET_AUTHS_ASSETS_ID", "INT", col_required=True)
    t.add("ASSET_AUTHS_PEOPLE_ID", "CHAR", col_size=50, col_required=True)
    t.add("ASSET_AUTHS_ENABLED", "INT", col_size=1)
    tables.append(t)

    indexes = []
    indexes.append(db.tables.index("ASSETS", ["ASSETS_NAME"], unique=True))
    indexes.append(db.tables.index("ASSET_LINKS", ["ASSET_LINKS_ASSETS_ID", "ASSET_LINKS_NAME"], unique=True))
    indexes.append(db.tables.index("ASSET_AUTHS", ["ASSET_AUTHS_ASSETS_ID", "ASSET_AUTHS_PEOPLE_ID"], unique=True))

    db.create(tables=tables, indexes=indexes)


def run():

    sql = "INSERT INTO LISTS (LISTS_NAME,LISTS_INTERNAL) VALUES (%s,1)"
    db.query(sql, ("ASSET LOCATIONS",), squelch=True)
    db.commit()
