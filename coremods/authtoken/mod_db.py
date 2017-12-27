from mod_def import mod_def

db = None


def init(hdb):
    global db
    db = hdb.db

    tables = []
    indexes = []

    for md in mod_def:
        md = mod_def[md]
        t = db.tables.table(md["TABLE"])
        for col in md["COLS"]:
            ftab = None
            fcol = None
            if col["TYPE"] == "ID":
                ftab = col["ID"]
                fcol = "{}_ID".format(col["ID"])
            t.add(col["NAME"],
                  col["TYPE"],
                  col_size=col.get("SIZE", None),
                  col_required=col.get("REQUIRED", False),
                  fk_table=ftab,
                  fk_col=fcol,
                  )
        for i in md["INDEX"]:
            indexes.append(db.tables.index(md["TABLE"], i, unique=False))
        for i in md["UNIQUE"]:
            indexes.append(db.tables.index(md["TABLE"], i, unique=True))

        tables.append(t)

    db.create(tables=tables, indexes=indexes)


def run():
    pass
