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


def parse_query(query, cols):
    sql = ""
    params = ()
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
            r = re.split("([=<>~]|!=)", q, 1)
            if len(r) > 2:
                field = r[0]
                op = r[1]
                vals = r[2].split("|")
                if field in cols and cols[field]["QUERY"] == 1:
                    sql += " {} ( 1=2".format(connector)
                    for val in vals:
                        sql == " OR {}{}%s".format(field, op)
                        params += (val,)
                        cnt += 1
                    sql += ")"
                    connector = "AND"
            else:
                q = "%{}%".format(q)
                sql += " {} ( 1=2".format(connector)
                for col in cols:
                    if cols[col]["SEARCH"] == 1:
                        sql += " OR {} LIKE %s".format(col)
                        params += (q,)
                sql += ")"
                connector = "AND"

    while open_par > 0:
        sql += ")"
        open_par -= 1

    return sql, params


def build_list_query(table, cols):
    query = haxdb.get("query")

    sql = """
    SELECT * FROM {}
    WHERE 1=1
    """
    params = (table,)

    if query:
        sqlext, paramsext = parse_query(query, cols)
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
        udf[uname] = row
    return udf


def get_cols(mod_def):
    udfs = get_udf(mod_def["NAME"])
    cols = {}
    headers = []

    for col in mod_def["COLS"]:
        cols[col["NAME"]] = col
        headers.append(col["NAME"])

    for udf in udfs:
        fieldname = "{}_UDF{}".format(mod_def["NAME"], udf["UDF_NUM"])
        col = {
            "CATEGORY": udf["UDF_CATEGORY"],
            "NAME": udf["UDF_NAME"],
            "HEADER": udf["UDF_HEADER"],
            "TYPE": udf["UDF_TYPE"],
            "EDIT": udf["UDF_EDIT"],
            "QUERY": udf["UDF_QUERY"],
            "SEARCH": udf["UDF_SEARCH"],
            "REQUIRED": udf["UDF_REQUIRED"],
            "DEFAULT": udf["UDF_DEFAULT"],
            "NEW": udf["UDF_NEW"],
            "AUTH": {
                "READ": col["UDF_READ"],
                "WRITE": col["UDF_WRITE"],
            }
        }
        cols[fieldname] = col
        headers.append(udf["UDF_NAME"])

    return headers, cols


def list_call(mod_def):
    headers, cols = get_cols(mod_def)

    sql, params = build_list_query(table, cols)
    cur = haxdb.db.query(sql, params)
    data = []
    for row in cur:
        newdata = {}
        for col in cols:
            newdata[col] = row[col]
        data.append(newdata)

    event_data = {
        "api": mod_def["NAME"],
        "call": "list",
        "query": haxdb.get("query"),
        "csv": haxdb.get("csv")
        "data": data,
    }
    haxdb.trigger("LIST.{}".format(mod_def["NAME"]), event_data)

    if haxdb.get("csv") == 1:
        return haxdb.func("FILE_CSV")(filename, headers, data)

    raw = {"data": data}
    return output(success=1, raw=raw)


def view_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")
    if not rowid:
        msg "MISSING PARAMETER: rowid"
        return output(success=0, message=msg)

    table = mod_def["NAME"]
    sql = "select * FROM {} WHERE {}_ID=%s".format(table, table)
    row = haxdb.db.qaf(sql, (rowid,))
    if not row:
        msg = "NO ROWS RETURNED"
        return output(success=0, message=msg)

    headers, cols = get_cols(mod_def)
    data = {}
    for col in cols:
        data[col] = row[col]

    event_data = {
        "api": mod_def["NAME"],
        "call": "view",
        "rowid": rowid,
        "data": data,
    }
    haxdb.trigger("VIEW.{}.{}".format(mod_def["NAME"], rowid), event_data)

    raw = {"data": data}
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
