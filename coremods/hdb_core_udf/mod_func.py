from PIL import Image

haxdb = None

def build_UDF():
    for table in haxdb.mod_def:
        mod = haxdb.mod_def[table]
        if "UDF" in mod and mod["UDF"] > 0:
            for i in range(0, mod["UDF"]):
                sql = """
                    INSERT INTO UDF (UDF_TABLE, UDF_NUM, UDF_NAME, UDF_ENABLED)
                    VALUES (%s, %s, %s, 0)
                    """
                udfname = "UDF{}".format(i)
                haxdb.db.query(sql, (table, i, udfname))
    haxdb.db.commit()


def extend_mod_def():
    for mname in haxdb.mod_def:
        cols = haxdb.mod_def[mname]["COLS"]
        for col in list(cols):
            if "UDF" in col and col["UDF"] == 1:
                haxdb.mod_def[mname]["COLS"].remove(col)

    sql = """
        SELECT * FROM UDF
        LEFT OUTER JOIN LISTS ON LISTS_ID=UDF_LISTS_ID
        WHERE UDF_ENABLED=1
        ORDER BY UDF_TABLE, UDF_NUM
        """
    r = haxdb.db.query(sql)
    if not r:
        return False
    for row in r:
        col = {
            "UDF": 1,
            "CATEGORY": row["UDF_CATEGORY"],
            "NAME": "{}_UDF{}".format(row["UDF_TABLE"], row["UDF_NUM"]),
            "HEADER": row["UDF_NAME"],
            "TYPE": row["UDF_TYPE"],
            "LIST_NAME": row["LISTS_NAME"],
            "ID_API": row["UDF_API"],
            "EDIT": 1,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": None,
            "NEW": 0,
            "AUTH": {
                "READ": row["UDF_AUTH_READ"],
                "WRITE": row["UDF_AUTH_WRITE"],
            }
        }
        haxdb.mod_def[row["UDF_TABLE"]]["COLS"].append(col)

def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    build_UDF()
    extend_mod_def()


def run():
    pass
