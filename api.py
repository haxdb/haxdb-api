from data import *
import shlex
import re

db = None


def init(app_db):
    global db
    db = app_db


def valid_value(col_type, val):
    if val is None:
        return True

    if col_type == "BOOL":
        try:
            if int(val) in (0, 1):
                return True
            else:
                return False
        except:
            return False

    if col_type == "INT":
        try:
            int(val)
        except:
            return False
        return True

    if col_type == "FLOAT":
        try:
            float(val)
        except:
            return False
        return True

    if col_type in ("TEXT", "STR", "LIST"):
        return True

    if col_type == "DATE":
        d = re.compile("\d\d\d\d\-\d{1,2}\-\d{1,2}")
        return d.match(val)

    return False


class api_call:
    NAME = ""
    TABLE = ""
    ROWID = ""
    COLS = []
    _COLS = {}
    UDF = {}
    ORDER = []

    def __init__(self, api_def):
        self.NAME = api_def["NAME"]
        self.TABLE = api_def["TABLE"]
        self.ROWID = api_def["ROWID"]
        self.COLS = api_def["COLS"]
        self.UDF = api_def["UDF"]
        self.ORDER = api_def["ORDER"]

        for col in self.COLS:
            self._COLS[col["NAME"]] = col

        if "CONTEXT_ID" not in self.UDF or not self.UDF["CONTEXT_ID"]:
            self.UDF["CONTEXT_ID"] = 0

    def context_id(self, id):
        self["UDF_CONTEXT_ID"] = id

    def get_list_id(self, list_name):
        return db.qaf("SELECT * FROM LISTS WHERE LISTS_NAME=%s", (list_name,))

    def get_lists(self, cols=None):
        cols = cols or self.get_cols()

        list_ids = []
        for col in cols:
            if col["TYPE"] == "LIST":
                if "LIST" in col:
                    list_ids.append(int(col["LIST"]))
                elif "LIST_NAME" in col:
                    list_id = self.get_list_id(col["LIST_NAME"])
                    if list_id:
                        list_ids.append(int(list_id))

        if not list_ids:
            return {}

        lists = {}

        sql = """
        SELECT LISTS.*, LIST_ITEMS.* FROM LISTS
        JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID
             AND LIST_ITEMS_ENABLED=1
        WHERE
        LISTS_ID IN ({})
        """.format(",".join(list_ids))

        sql += " ORDER BY LIST_ITEMS_ORDER"
        row = db.qaf(sql, params)
        while row:
            lname = row["LISTS_NAME"]
            if lname not in lists:
                lists[lname] = []
            list_item = {
                "VALUE": row["LIST_ITEMS_VALUE"],
                "DESCRIPTION": row["LIST_ITEMS_DESCRIPTION"],
            }
            lists[lname].append(list_item)
            row = db.next()

        return lists

    def get_cols(self):
        cols = self.COLS

        sql = """
        SELECT UDF_NAME, UDF_TYPE, UDF_LISTS_ID FROM UDF
        WHERE UDF_CONTEXT=%s and UDF_CONTEXT_ID=%s and UDF_ENABLED=1
        ORDER BY UDF_ORDER
        """
        row = db.qaf(sql, (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"], ))
        while row:
            col = {
                    "UDF_ID": row["UDF_ID"],
                    "NAME": row["UDF_NAME"],
                    "HEADER": row["UDF_NAME"],
                    "TYPE": row["UDF_TYPE"],
                    "QUERY": 1,
                    "SEARCH": 1,
                    "REQUIRED": 0,
                  }
            if row["UDF_TYPE"] == "LIST":
                col["LIST"] = row["UDF_LISTS_ID"]

            cols.append(col)
            row = db.next()

        return cols

    def build_query(self, query):
        sql = ""
        if query:
            queries = shlex.split(query)
            for query in queries:
                opreg = re.compile("([!=><])")
                qs = opreg.split(query)
                if len(qs) > 1:
                    col = qs[0]
                    op = qs[1]
                    if op == "!":
                        op = "!="
                    vals = qs[2].split("|")
                    if col in self._COLS and self._COLS[col]["QUERY"]:
                        sql += " AND ("
                        valcount = 0
                        for val in vals:
                            if valcount > 0:
                                sql += " OR "

                            if val == "NULL" and op == "=":
                                sql += "%s IS NULL" % (col,)
                            elif val == "NULL" and op == "!=":
                                sql += "%s IS NOT NULL" % (col,)
                            else:
                                sql += "{} {} %s".format(col, op)
                                params += (val,)

                            valcount += 1

                        sql += ")"
                    else:
                        sql += " AND ("
                        valcount = 0
                        for val in vals:
                            if valcount > 0:
                                sql += " OR "
                            if val == "NULL" and op == "=":
                                sql += "("
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ENABLED=1 and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1) < 1"
                                sql += " OR "
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ENABLED=1 and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1 and UDF_DATA_VALUE IS NULL) > 0"
                                sql += ")"
                                params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"])
                                params += (col,)
                                params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"])
                                params += (col,)
                            elif val == "NULL" and op == "!=":
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ENABLED=1 and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1) > 0"
                                params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"])
                                params += (col,)
                            else:
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ENABLED=1 and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1 and UDF_DATA_VALUE {} %s) > 0".format(op)
                                params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"])
                                params += (col, val,)
                            valcount += 1
                        sql += ")"

                else:
                    query = "%" + query + "%"
                    sql += " AND ("
                    valcount = 0

                    for col in self.COLS:
                        if col["SEARCH"]:
                            if valcount > 0:
                                sql += " OR "
                                sql += " {} LIKE %s ".format(col)
                                params += (query,)
                                valcount += 1

                    sql += " OR (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ENABLED=1 and UDF_ID=UDF_DATA_UDF_ID and UDF_ENABLED=1 and UDF_DATA_VALUE LIKE %s) > 0"
                    params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"], query)
                    sql += ")"

    def list_call(self, sql=None, params=None, calc_row_function=None, query=None, meta=None):
        sql = sql or "SELECT * FROM {}".format(self.TABLE)
        params = params or ()
        query = query or var.get("query")

        meta = meta or {}
        meta["api"] = self.NAME
        meta["action"] = "list"
        meta["query"] = query
        meta["cols"] = self.get_cols()
        meta["lists"] = self.get_lists(meta["cols"])

        sql += """
        LEFT OUTER JOIN UDF ON UDF_CONTEXT=%s
                        AND UDF_CONTEXT_ID=%s
                        AND UDF_ENABLED=1
        LEFT OUTER JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
                        AND UDF_DATA_ROWID={}
        """.format(self.ROWID)
        params += (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"])

        sql += " WHERE 1=1"
        sql += self.build_query(query)

        if len(self.ORDER) > 0:
            sql += " ORDER BY {},{}".format(self.ROWID, ",".join(self.ORDER))

        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        rows = []
        rowdata = None
        lastrowid = None
        while row:
            row = dict(row)
            if calc_row_function:
                row = calc_row_function(dict(row))

            rowid = row[self.udf_rowid]
            if rowid != lastrowid:
                if rowdata:
                    rows.append(rowdata)
                rowdata = {}
                lastrowid = rowid
            rowdata.update(row)
            if row["UDF_NAME"]:
                rowdata[row["UDF_NAME"]] = row["UDF_DATA_VALUE"]

            row = db.next()

        if rowdata:
            rows.append(rowdata)

        return output(success=1, data=rows, meta=meta)

    def view_call(self, sql=None, params=None, calc_row_function=None, rowid=None, meta=None):
        params = params or ()
        rowid = rowid or var.get("rowid")
        meta = meta or {}

        if not sql:
            sql = "SELECT * FROM {} WHERE {}=%s".format(self.TABLE, self.ROWID)
            params = (rowid,)

        meta["api"] = self.NAME
        meta["action"] = "view"
        meta["cols"] = self.get_cols()
        meta["lists"] = self.get_lists(meta["cols"])

        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)

        if not row:
            return output(success=0, meta=meta, message="NO DATA")

        row = dict(row)
        if self.udf_context:
            udf_sql = """
            SELECT * FROM UDF
            JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
            WHERE
            UDF_CONTEXT=%s and UDF_CONTEXT_ID=%s AND UDF_DATA_ROWID=%s
            AND UDF_ENABLED=1
            ORDER BY UDF_ORDER
            """
            udf_params = (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"], self.ROWID)
            db.query(udf_sql, udf_params)
            udf = db.next()
            while udf:
                row[udf["UDF_NAME"]] = udf["UDF_DATA_VALUE"]
                udf = db.next()

        if calc_row_function:
            row = calc_row_function(dict(row))
        return output(success=1, meta=meta, data=row)

    def new_call(self, sql=None, params=None, meta=None):
        params = params or ()

        meta = meta or {}
        meta["api"] = self.NAME
        meta["action"] = "new"

        if not sql:
            col_names = []
            col_params = ()
            udf_names = []
            udf_params = []
            cols = self.get_cols()

            errors = ""
            for col in cols:
                val = var.get(col)
                if val is not None:
                    if valid_value(col["TYPE"], val):
                        if col["NAME"] in self._COLS:
                            col_names.append(col["NAME"])
                            col_params += (val,)
                        else:
                            udf_names.append(col["NAME"])
                            udf_params.append(val)
                    else:
                        errors += "INVALID VALUE FOR {}\n".format(col["NAME"])
                elif col["REQUIRED"] == 1:
                    errors += "{} IS REQUIRED.\n".format(col["NAME"])

        if errors:
            return output(success=0, meta=meta, message=errors)

        sql = """
        INSERT INTO {} ({})
        VALUES ({})
        """.format(self.TABLE, ",".join(col_names), ",".join(["%s"*len(col_names)]))
        db.query(sql, params)

        if db.error:
            return output(success=0, meta=meta, message=db.error)

        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            meta["rowid"] = db.lastrowid
            if udf_names:
                sql = "DELETE FROM UDF WHERE UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s and UDF_ROWID=%s"
                db.query(sql, (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"], meta["rowid"]))
                for udf_key in udf_names.keys():
                    udf_name = udf_names[udf_key]
                    udf_val = udf_params[udf_key]
                    sql = "INSERT INTO UDF (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_NAME, UDF_ROWID) VALUES (%s, %s, %s, %s)"
                    db.query(sql, (self.UDF["CONTEXT"], self.UDF["CONTEXT_ID"], udf_name, udf_val))
                    if db.error:
                        return output(success=0, meta=meta, message=db.error)
            db.commit()
            return output(success=1, meta=meta, message="{} ROWS CREATED".format(meta["rowcount"]), value=db.lastrowid)

        return output(success=0, meta=meta, message="NO ROWS CREATED")

    def delete_call(self, sql=None, params=None, meta=None, rowid=None):
        meta = meta or {}
        meta["api"] = self.NAME
        meta["action"] = "delete"

        if not sql:
            rowid = rowid or var.get("rowid")
            sql = "DELETE FROM {} WHERE {}=%s".format(self.TABLE, self.ROWID)
            params = (rowid,)

        db.query(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)

        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            db.commit()
            return output(success=1, meta=meta, message="DELETED")

        return output(success=0, meta=meta, message="NO ROWS DELETED")

    def save_call(self, meta=None, rowid=None):
        rowid = rowid or var.get("rowid")

        col_names = []
        col_params = ()
        udf_names = []
        udf_params = []
        cols = self.get_cols()

        errors = ""
        for col in cols:
            val = var.get(col)
            if val is not None:
                if valid_value(col["TYPE"], val):
                    if col["NAME"] in self._COLS:
                        col_names.append("{}=%s".format(col["NAME"]))
                        col_params += (val,)
                    else:
                        udf_names.append(col["NAME"])
                        udf_params.append(val)
                else:
                    errors += "INVALID VALUE FOR {}\n".format(col["NAME"])

        if errors:
            return output(success=0, meta=meta, message=errors)

        meta["rowcount"] = 0
        if col_names:
            sql = "UPDATE {} SET {} WHERE {}=%s".format(self.TABLE, ",".join(col_names), self.ROWID)
            params = (rowid,)
            db.query(sql, params)
            if db.error:
                return output(success=0, meta=meta, message=db.error)
            meta["rowcount"] = db.rowcount

        if udf_names:
            for udf_key in udf_names.keys():
                udf_name = udf_names[udf_key]
                udf_val = udf_params[udf_key]
                sql = "DELETE FROM UDF_DATA WHERE UDF_DATA_UDF_ID and UDF_ROWID=%s"
                db.query(sql, (cols[udf_name]["UDF_ID"], rowid))
                sql = "INSERT INTO UDF_DATA (UDF_DATA_UDF_ID, UDF_DATA_VALUE, UDF_DATA_ROWID) VALUES (%s, %s, %s)"
                db.query(sql, (cols[udf_name]["UDF_ID"], udf_val, rowid))
                if db.error:
                    return output(success=0, meta=meta, message=db.error)
                meta["rowcount"] = meta["rowcount"] or db.rowcount

        if meta["rowcount"] > 0:
            return output(success=1, meta=meta, message="SAVED")

        return output(success=0, meta=meta, message="NOTHING UPDATED")
