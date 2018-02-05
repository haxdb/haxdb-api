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

    if col_type in ("CHAR", "TEXT", "LIST"):
        return True

    if col_type == "DATE":
        r = "^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$"
        d = re.compile(r)
        return d.match(val)

    return False


def parse_query(query, cols):
    sql = ""
    params = ()
    query = query.replace("(", " ( ")
    query = query.replace(")", " ) ")
    query = shlex.split(query)
    connector = "AND"
    use_connector = True
    open_par = 0
    for q in query:
        if q == "(":
            open_par += 1
            if use_connector:
                sql += "{} ".format(connector)
                connector = "AND"
            sql += "("
            use_connector = False
        elif q == ")":
            open_par -= 1
            sql += ")"
            use_connector = True
        elif q.upper() == "OR":
            connector = "OR"
            use_connector = True
        elif q.upper() == "AND":
            connector = "AND"
            use_connector = True
        else:
            r = re.split("([=<>~]|!=)", q, 1)
            if len(r) > 2:
                field = r[0]
                op = r[1]
                vals = r[2].split("|")
                if op == "~":
                    op = " LIKE "
                    newvals = []
                    for val in vals:
                        newvals.append(val.replace("*", "%"))
                    vals = newvals
                if field in cols and cols[field]["QUERY"] == 1:
                    if use_connector:
                        sql += "{} ".format(connector)
                        connector = "AND"
                    sql += " ("
                    valnum = 0
                    for val in vals:
                        if valnum > 0:
                            sql += " OR "
                        valnum += 1
                        if val.upper() == "NULL" and op == "=":
                            sql += " {} IS NULL".format(field)
                        elif val.upper() == "NULL" and op == "!=":
                            sql += " {} IS NOT NULL".format(field)
                        else:
                            sql += " {}{}%s".format(field, op)
                            params += (val,)
                    sql += ")"
                    use_connector = True
            else:
                if use_connector:
                    sql += "{} ".format(connector)
                    connector = "AND"
                q = "%{}%".format(q)
                sql += " ( 1=2"
                for col in cols:
                    if cols[col]["SEARCH"] == 1:
                        sql += " OR {} LIKE %s".format(col)
                        params += (q,)
                sql += ")"
                use_connector = True

    while open_par > 0:
        sql += ")"
        open_par -= 1

    return sql, params


def get_joins(cols):
    i = 0
    joins = {}
    for cname in cols:
        col = cols[cname]
        if (col["TYPE"] == "ID" and
           col["ID_API"] and
           haxdb.mod_def[col["ID_API"]]):
            joins[col["NAME"]] = {
                "alias": "J{}".format(i),
                "api": col["ID_API"],
                "rowname": haxdb.mod_def[col["ID_API"]]["ROWNAME"],
            }
            i += 1

    return joins


def build_list_query(table, cols, joins):
    query = haxdb.get("query")

    sql = "SELECT T0.*"
    for jcolname in joins:
        j = joins[jcolname]
        if isinstance(j["rowname"], list):
            for jv in j["rowname"]:
                sql += ",{}.{} as {}_{}".format(j["alias"], jv, j["alias"], jv)
        else:
            sql += ",{}.{} as {}_{}".format(j["alias"], j["rowname"],
                                            j["alias"], j["rowname"])

    sql += " FROM {} T0".format(table)
    for jcolname in joins:
        j = joins[jcolname]
        sql += """
        LEFT OUTER JOIN {} {} ON T0.{}={}.{}_ID
        """.format(j["api"], j["alias"], jcolname, j["alias"], j["api"])
    sql += " WHERE 1=1".format(table)
    params = ()

    if query:
        sqlext, paramsext = parse_query(query, cols)
        sql = "{} {}".format(sql, sqlext)
        params += paramsext

    return sql, params


def build_rowname(rdef, data, prefix=""):
    rowname = ""
    if isinstance(rdef, list):
        for col in rdef:
            r = data["{}{}".format(prefix, col)] or ""
            rowname += " {}".format(r)
    else:
        r = data["{}{}".format(prefix, rdef)] or ""
        rowname += r
    rowname = rowname.strip()
    return rowname


def get_col(mod_def, colname):
    for col in mod_def["COLS"]:
        if col["NAME"] == colname:
            return col
    return None


def get_cols(mod_def, rperm=None, wperm=None):
    dba = haxdb.session("dba")
    table = mod_def["NAME"]
    cols = {
        "{}_ID".format(table): {
            "CATEGORY": "ROW",
            "NAME": "{}_ID".format(table),
            "HEADER": "{}_ID".format(table),
            "TYPE": "INT",
            "EDIT": 0,
            "QUERY": 1,
            "SEARCH": 0,
            "REQUIRED": 0,
            "DEFAULT": 0,
            "NEW": 0,
            "AUTH": {
                "READ": mod_def["AUTH"]["READ"],
                "WRITE": mod_def["AUTH"]["WRITE"],
            }
        }
    }
    headers = ["{}_ID".format(table)]

    for col in mod_def["COLS"]:
        colrperm = col["AUTH"]["READ"]
        if not colrperm:
            colrperm = 0
        colwperm = col["AUTH"]["WRITE"]
        if not colwperm:
            colwperm = 0
        if ((rperm is None or rperm >= colrperm) and
           (wperm is None or wperm >= colwperm) and
           (col["NAME"] not in headers)):
                cols[col["NAME"]] = col
                headers.append(col["NAME"])

    return headers, cols


def list_call(mod_def):
    table = mod_def["NAME"]
    api_perm = int(mod_def["AUTH"]["READ"])
    user_perm = haxdb.func("PERM:GET")(table, "READ")
    if api_perm > user_perm:
        msg = "INVALID PERMISSIONS"
        return haxdb.response(success=0, message=msg)

    headers, cols = get_cols(mod_def, rperm=user_perm)

    joins = get_joins(cols)
    sql, params = build_list_query(table, cols, joins)
    cur = haxdb.db.query(sql, params)
    if not cur:
        msg = "QUERY MALFORMED"
        return haxdb.response(success=0, message=msg)

    data = []
    for row in cur:
        newdata = {}
        for col in cols:
            newdata[col] = row[col]

        for jcolname in joins:
            j = joins[jcolname]
            nid = "{}:ROWNAME".format(jcolname)
            newdata[nid] = build_rowname(j["rowname"], row, j["alias"]+"_")

        newdata["ROWID"] = row["{}_ID".format(table)]
        rdef = haxdb.mod_def[table]["ROWNAME"]
        newdata["ROWNAME"] = build_rowname(rdef, row)
        data.append(newdata)

    event_data = {
        "api": mod_def["NAME"],
        "call": "list",
        "query": haxdb.get("query"),
        "csv": haxdb.get("csv"),
        "data": data,
    }
    haxdb.trigger("LIST.{}".format(mod_def["NAME"]), event_data)

    if haxdb.get("csv") == 1:
        return haxdb.func("FILE_CSV")(filename, headers, data)

    raw = {"api": table, "data": data}
    return haxdb.response(success=1, raw=raw)


def view_call(mod_def, rowid=None):
    table = mod_def["NAME"]
    api_perm = int(mod_def["AUTH"]["READ"])
    user_perm = haxdb.func("PERM:GET")(table, "READ")
    if api_perm > user_perm:
        msg = "INVALID PERMISSIONS"
        return haxdb.response(success=0, message=msg)

    headers, cols = get_cols(mod_def, rperm=user_perm)
    joins = get_joins(cols)
    rowid = rowid or haxdb.get("rowid")
    if not rowid:
        msg = "MISSING PARAMETER: rowid"
        return haxdb.response(success=0, message=msg)

    sql = "select * "
    for jcolname in joins:
        j = joins[jcolname]
        if isinstance(j["rowname"], list):
            for jv in j["rowname"]:
                sql += ",{}.{} as {}_{}".format(j["alias"], jv, j["alias"], jv)
        else:
            sql += ",{}.{} as {}_{}".format(j["alias"], j["rowname"],
                                            j["alias"], j["rowname"])

    sql += " FROM {} T0 ".format(table)
    for jcolname in joins:
        j = joins[jcolname]
        sql += """
        LEFT OUTER JOIN {} {} ON T0.{}={}.{}_ID
        """.format(j["api"], j["alias"], jcolname, j["alias"], j["api"])
    sql += " WHERE T0.{}_ID=%s".format(table)
    row = haxdb.db.qaf(sql, (rowid,))
    if not row:
        msg = "NO ROWS RETURNED"
        return haxdb.response(success=0, message=msg)

    data = {}
    for col in cols:
        data[col] = row[col]

    for jcolname in joins:
        j = joins[jcolname]
        nid = "{}:ROWNAME".format(jcolname)
        data[nid] = build_rowname(j["rowname"], row, j["alias"]+"_")

    event_data = {
        "api": mod_def["NAME"],
        "call": "view",
        "rowid": rowid,
        "data": data,
    }
    haxdb.trigger("VIEW.{}.{}".format(mod_def["NAME"], rowid), event_data)

    raw = {"api": table, "data": data}
    return haxdb.response(success=1, raw=raw)


def new_call(mod_def, defaults=None, values=None):
    table = mod_def["NAME"]

    insert_perm = int(mod_def["AUTH"]["INSERT"])
    if not haxdb.func("PERM:HAS")(table, "INSERT", insert_perm):
        msg = "INVALID PERMISSIONS"
        return haxdb.response(success=0, message=msg)

    data = {}

    # set defaults from mod_def
    for col in mod_def["COLS"]:
        if "DEFAULT" in col:
            data[col["NAME"]] = col["DEFAULT"]

    # set any defaults passed in
    if defaults:
        for key in defaults:
            data[key] = defaults[key]

    # set user passed data
    for col in mod_def["COLS"]:
        val = haxdb.get("new[{}]".format(col["NAME"]))
        if val:
            data[col["NAME"]] = val

    # override values with any values passed in
    if values:
        for key in values:
            data[key] = values[key]

    cols = []
    binds = []
    vals = []
    for col in mod_def["COLS"]:
        if col["NAME"] in data:
            if not valid_value(col, val):
                msg = "INVALID VALUE FOR {}".format(col["NAME"])
                return haxdb.response(success=0, message=msg)

    for key in data:
        cols.append(key)
        binds.append("%s")
        vals.append(data[key])

    sql = """
    INSERT INTO {} ({}) VALUES ({})
    """.format(table, ",".join(cols), ",".join(binds))
    r = haxdb.db.query(sql, vals)

    if not r:
        msg = haxdb.db.error
        return haxdb.response(success=0, message=msg)

    haxdb.db.commit()

    event_data = {
        "api": mod_def["NAME"],
        "call": "new",
        "data": data,
        "rowid": haxdb.db.lastrowid,
    }
    haxdb.trigger("NEW.{}".format(mod_def["NAME"]), event_data)

    raw = {
        "api": table,
        "rowid": haxdb.db.lastrowid,
    }
    return haxdb.response(success=1, message="CREATED", raw=raw)


def save_call(mod_def, rowid=None, values=None):
    rowid = rowid or haxdb.get("rowid")
    table = mod_def["NAME"]
    data = {}

    if not rowid:
        msg = "MISSING INPUT: rowid"
        return haxdb.response(success=0, message=msg)

    # set value from user
    for col in mod_def["COLS"]:
        val = haxdb.get("save[{}]".format(col["NAME"]))
        if val is not None:
            if col["EDIT"] != 1:
                msg = "{} IS NOT EDITABLE".format(col["NAME"])
                return haxdb.response(success=0, message=msg)
            write_perm = col["AUTH"]["WRITE"]
            if not haxdb.func("PERM:HAS")(table, "WRITE", write_perm):
                msg = "INVALID PERMISSIONS"
                return haxdb.response(success=0, message=msg)
            data[col["NAME"]] = val

    # override values with any values passed in
    if values:
        for key in values:
            data[key] = values[key]

    if len(data) <= 0:
        msg = "NOTHING TO SAVE"
        return haxdb.response(success=0, message=msg)

    params = ()
    sql = "UPDATE {} SET".format(table)
    for colname in data:
        col = get_col(mod_def, colname)
        if not valid_value(col, data[colname]):
            msg = "INVALID VALUE FOR: {}".format(colname)
            return haxdb.response(success=0, message=msg)
        if not data[colname]:
            sql += " {}=NULL".format(colname)
        else:
            sql += " {}=%s".format(colname)
            params += (data[colname],)
    sql += " WHERE {}_ID=%s".format(table)
    params += (rowid,)

    r = haxdb.db.query(sql, params)
    if not r:
        msg = haxdb.db.error
        return haxdb.response(success=0, message=msg)

    haxdb.db.commit()

    event_data = {
        "api": mod_def["NAME"],
        "call": "save",
        "rowid": rowid,
    }
    haxdb.trigger("SAVE.{}.{}".format(mod_def["NAME"], rowid), event_data)

    raw = {
        "api": table,
        "rowid": rowid,
        "data": data,
    }
    return haxdb.response(success=1, message="SAVED", raw=raw)


def delete_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")
    table = mod_def["NAME"]

    delete_perm = int(mod_def["AUTH"]["DELETE"])
    if not haxdb.func("PERM:HAS")(table, "DELETE", delete_perm):
        msg = "INVALID PERMISSIONS"
        return haxdb.response(success=0, message=msg)

    if isinstance(rowid, list):
        sql = """
            DELETE FROM {} WHERE {}_ID IN ({})
        """.format(table, table, ",".join(["%s"]*len(rowid)))
        params = tuple(rowid)
    else:
        sql = "DELETE FROM {} WHERE {}_ID=%s".format(table, table)
        params = (rowid,)
    r = haxdb.db.query(sql, params)
    if not r:
        msg = haxdb.db.error
        return haxdb.response(success=0, message=msg)

    haxdb.db.commit()

    event_data = {
        "api": mod_def["NAME"],
        "call": "delete",
        "rowid": rowid,
        "rowcount": haxdb.db.rowcount,
    }
    haxdb.trigger("DELETE.{}.{}".format(mod_def["NAME"], rowid), event_data)

    raw = {
        "api": table,
        "rowid": rowid,
        "rowcount": haxdb.db.rowcount,
    }
    msg = "DELETED {} ROWS".format(haxdb.db.rowcount)
    return haxdb.response(success=1, message=msg, raw=raw)
