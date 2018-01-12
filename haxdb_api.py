from flask import make_response, request
import shlex
import re
import os.path

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def valid_value(col, val):
    if val == '':
        return True

    col_type = col["TYPE"]

    if val is None:
        return True

    if col_type == "SELECT":
        if "OPTIONS" not in col or val not in col["OPTIONS"]:
            return False
        return True

    if col_type == "BOOL":
        try:
            if int(val) in (0, 1):
                return True
            else:
                return False
        except (ValueError, TypeError) as e:
            return False

    if col_type == "INT" or col_type == "ID" or col_type == "TIMESTAMP":
        try:
            int(val)
        except (ValueError, TypeError) as e:
            return False
        return True

    if col_type == "FLOAT":
        try:
            float(val)
        except (ValueError, TypeError) as e:
            return False
        return True

    if col_type in ("TEXT", "LIST"):
        return True

    if col_type == "DATE":
        r = "^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$"
        d = re.compile(r)
        return d.match(val)


def parse_query(query, valid_cols):
    # = equal
    # ! not equal
    # > greater than
    # < less than
    # ~ like (can use wildcards * or %)
    ops = "=!<>~"

    sql = ""
    query = query.replace("(", " ( ")
    query = query.replace(")", " ) ")
    query = shlex.split(query)
    connector = "AND"

    open_par = 0
    for q in query:
        if q == "(":
            open_par += 1
            sql += "{} (".format(connector)
            connector = "AND"
        elif q == ")":
            open_par -= 1
            sql += ")"
        elif q.upper() == "OR":
            connector = "OR"
        else:
            r = re.split(ops, q)
            if len(r) > 2:
                pass
            else:
                q = "%{}%".format(q)


    while open_par > 0:
        sql += ")"
        open_par -= 1

    return sql


def build_list_query(table, cols, udf):
    query = haxdb.get("query")

    valid_cols = set(cols)
    for u in udf:
        valid_cols.append(udf[u])

    sql = """
    SELECT * FROM {}
    WHERE 1=1
    """
    params = (table,)

    if query:
        sqlext, paramsext = parse_query(query, valid_cols)
        sql = "{} {}".format(sql, sqlext)
        params += paramsext

    return sql, params


def get_udf(table):
    udf = {}
    sql = """
    SELECT * FROM UDF WHERE UDF_TABLE=%s AND UDF_ENABLED=1
    """
    cur = haxdb.db.query(sql, (table,))
    for row in cur:
        uname = "{}_FIELD{}".format(table, row["UDF_NUM"])
        udf[uname] = row["UDF_NAME"]
    return udf


def get_cols(mod_def):
    cols = []
    for col in mod_def["COLS"]:
        cols.append(col["NAME"])
    return COLS


def list_call(mod_def):
    csv = haxdb.get("csv")

    udf = get_udf(table)
    cols = get_cols(mod_def)

    sql, params = build_list_query(table, cols, udf)
    cur = haxdb.db.query(sql, params)
    data = []
    for row in cur:
        newdata = {}
        for col in cols:
            newdata[col] = row[col]
        for  col in udf:
            newdata[udf[col]] = row[col]
        data.append(newdata)

    if csv == 1:
        return haxdb.func("FILE_CSV")(filename, headers, rows)

    event_data = {
        "api": mod_def["NAME"],
        "call": "list",
        "data": data,
    }
    haxdb.trigger("LIST.{}".format(mod_def["NAME"]), event_data)

    raw = {"data": data}
    return output(success=1, raw=raw)


def view_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")
    raw = {}
    return output(success=1, raw=raw)

def new_call(mod_def, defaults=None):
    raw = {}
    return output(success=1, raw=raw)

def delete_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")
    raw = {}
    return output(success=1, raw=raw)

def save_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")
    raw = {}
    return output(success=1, raw=raw)
