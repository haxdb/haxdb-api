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

def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    build_UDF()


def run():
    pass
