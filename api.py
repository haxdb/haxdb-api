from flask import make_response, request
import shlex
import re
import os.path

haxdb = None
db = None
output = None


def init(app_haxdb):
    global haxdb, db, output
    haxdb = app_haxdb
    db = haxdb.db
    output = haxdb.output


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

    if col_type in ("TEXT", "STR", "LIST", "ASCII"):
        return True

    if col_type == "DATE":
        d = re.compile("\d\d\d\d\-\d{1,2}\-\d{1,2}")
        return d.match(val)

    return False


class api_call:
    API_NAME = None
    API_ROWID = None
    API_CONTEXT_ID = 0
    COLS = []
    _COLS = {}
    ORDER = []

    def __init__(self, api_def):
        self.API_NAME = api_def["NAME"]
        self.API_ROWID = api_def["ROWID"]
        self.COLS = api_def["COLS"]
        self.ORDER = api_def["ORDER"]
        for col in self.COLS:
            if "CATEGORY" not in col:
                col["CATEGORY"] = "PRIMARY"
            self._COLS[col["NAME"]] = col

    def is_udf(self, col):
        if "UDF" in col and col["UDF"] == 1:
            return True
        return False

    def get_meta(self, action=None):
        meta = {}
        meta["api"] = self.API_NAME
        meta["action"] = action
        meta["col_rowid"] = self.API_ROWID
        meta["cols"] = self.get_cols()
        meta["lists"] = self.get_lists(meta["cols"])
        return meta

    def get_list_id(self, list_name):
        row = db.qaf("SELECT * FROM LISTS WHERE LISTS_NAME=%s", (list_name,))
        if row:
            return row["LISTS_ID"]
        return None

    def get_lists(self, cols=None):
        cols = cols or self.get_cols()

        list_ids = ()
        for col in cols:
            if col["TYPE"] == "LIST":
                if "LIST" in col:
                    try:
                        list_id = int(col["LIST"])
                    except (ValueError, TypeError) as e:
                        list_id = 0
                    if list_id not in list_ids:
                        list_ids += (list_id, )
                elif "LIST_NAME" in col:
                    list_id = self.get_list_id(col["LIST_NAME"])
                    if list_id and list_id not in list_ids:
                        list_ids += (int(list_id),)
        if not list_ids:
            return {}

        lists = {}

        sql = """
        SELECT LISTS.*, LIST_ITEMS.* FROM LISTS
        JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID
             AND LIST_ITEMS_ENABLED=1
        WHERE
        LISTS_ID IN ({})
        """.format(",".join(("%s",) * len(list_ids)))

        sql += " ORDER BY LIST_ITEMS_ORDER"
        row = db.qaf(sql, list_ids)
        while row:
            lname = row["LISTS_NAME"]
            lid = row["LISTS_ID"]
            if lid not in lists:
                lists[lid] = {"name": lname, "items": []}
            list_item = {
                "ID": row["LIST_ITEMS_ID"],
                "VALUE": row["LIST_ITEMS_VALUE"],
                "DESCRIPTION": row["LIST_ITEMS_DESCRIPTION"],
            }
            lists[lid]["items"].append(list_item)
            row = db.next()

        return lists

    def get_cols(self):
        cols = list(self.COLS)

        sql = """
        SELECT
        UDF_ID, UDF_NAME, UDF_TYPE,
        UDF_LISTS_ID, UDF_CATEGORY, UDF_API
        FROM UDF
        WHERE UDF_CONTEXT=%s and UDF_CONTEXT_ID=%s and UDF_ENABLED=1
        ORDER BY UDF_ORDER
        """
        row = db.qaf(sql, (self.API_NAME, self.API_CONTEXT_ID, ))
        while row:
            col = {
                    "UDF": 1,
                    "UDF_ID": row["UDF_ID"],
                    "NAME": row["UDF_NAME"],
                    "CATEGORY": row["UDF_CATEGORY"],
                    "HEADER": row["UDF_NAME"],
                    "TYPE": row["UDF_TYPE"],
                    "QUERY": 1,
                    "SEARCH": 1,
                    "REQUIRED": 0,
                    "EDIT": 1,
                  }
            if row["UDF_TYPE"] == "LIST":
                col["LIST"] = row["UDF_LISTS_ID"]
            if row["UDF_TYPE"] == "ID":
                col["ID_API"] = row["UDF_API"]

            cols.append(col)
            row = db.next()

        return cols

    def build_query(self, query):
        params = ()
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
                                sql += "HDB_LIST.{} IS NULL".format(col)
                            elif val == "NULL" and op == "!=":
                                sql += "HDB_LIST.{} IS NOT NULL".format(col)
                            else:
                                sql += "HDB_LIST.{} {} %s".format(col, op)
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
                                sql += """
                                (
                                    (SELECT COUNT(*)
                                    FROM UDF, UDF_DATA
                                    WHERE UDF_CONTEXT=%s
                                    AND UDF_CONTEXT_ID=%s
                                    and UDF_ENABLED=1
                                    and UDF_ID=UDF_DATA_UDF_ID
                                    and UDF_NAME=%s
                                    and UDF_DATA_ROWID={}
                                    and UDF_ENABLED=1) < 1
                                OR
                                    (SELECT COUNT(*)
                                    FROM UDF, UDF_DATA
                                    WHERE UDF_CONTEXT=%s
                                    AND UDF_CONTEXT_ID=%s
                                    and UDF_ENABLED=1
                                    and UDF_ID=UDF_DATA_UDF_ID
                                    and UDF_NAME=%s
                                    and UDF_ENABLED=1
                                    and UDF_DATA_VALUE IS NULL
                                    and UDF_DATA_ROWID={}) > 0
                                )""".format(self.API_ROWID, self.API_ROWID)
                                params += (self.API_NAME, self.API_CONTEXT_ID)
                                params += (col,)
                                params += (self.API_NAME, self.API_CONTEXT_ID)
                                params += (col,)
                            elif val == "NULL" and op == "!=":
                                sql += """
                                    (
                                    SELECT COUNT(*)
                                    FROM UDF, UDF_DATA
                                    WHERE UDF_CONTEXT=%s
                                    AND UDF_CONTEXT_ID=%s
                                    and UDF_ENABLED=1
                                    and UDF_ID=UDF_DATA_UDF_ID
                                    and UDF_NAME=%s
                                    and UDF_ENABLED=1
                                    and UDF_DATA_ROWID={}) > 0
                                """.format(self.API_ROWID)
                                params += (self.API_NAME, self.API_CONTEXT_ID)
                                params += (col,)
                            else:
                                sql += """
                                 (
                                 SELECT COUNT(*)
                                 FROM UDF, UDF_DATA
                                 WHERE UDF_CONTEXT=%s
                                 AND UDF_CONTEXT_ID=%s
                                 and UDF_ENABLED=1
                                 and UDF_ID=UDF_DATA_UDF_ID
                                 and UDF_NAME=%s
                                 and UDF_ENABLED=1
                                 and UDF_DATA_VALUE {} %s
                                 and UDF_DATA_ROWID={}) > 0
                                 """.format(op, self.API_ROWID)
                                params += (self.API_NAME, self.API_CONTEXT_ID)
                                params += (col, val,)
                            valcount += 1
                        sql += ")"
                else:
                    query = "%" + query + "%"
                    sql += " AND ("
                    valcount = 0

                    for col in self.COLS:
                        if col["NAME"] in self._COLS and col["SEARCH"] == 1:
                            if valcount > 0:
                                sql += " OR "
                            sql += " {} LIKE %s ".format(col["NAME"])
                            params += (query,)
                            valcount += 1
                    if valcount > 0:
                        sql += " OR "
                    sql += """
                    (SELECT COUNT(*)
                    FROM UDF, UDF_DATA
                    WHERE UDF_CONTEXT=%s
                    AND UDF_CONTEXT_ID=%s
                    and UDF_ENABLED=1
                    and UDF_ID=UDF_DATA_UDF_ID
                    and UDF_ENABLED=1
                    and UDF_DATA_VALUE LIKE %s
                    and UDF_DATA_ROWID={}) > 0
                    """.format(self.API_ROWID)
                    params += (self.API_NAME, self.API_CONTEXT_ID, query)
                    sql += ")"
        return sql, params

    def csv_out(self, rows, headers=None):
        import csv
        from datetime import datetime
        from StringIO import StringIO

        if not headers:
            cols = self.get_cols()
            headers = []
            for col in cols:
                headers.append(col["NAME"])

        csvfile = StringIO()
        writer = csv.DictWriter(csvfile,
                                fieldnames=headers,
                                extrasaction='ignore')
        writer.writeheader()
        numrows = 0
        for row in rows:
            numrows += 1
            writer.writerow(row)

        filedata = csvfile.getvalue()
        now = datetime.now().strftime("%Y%m%d%H%M")
        filename = "{}.{}.csv".format(self.API_NAME, now)

        event_data = {
            "api": self.API_NAME,
            "call": "csv",
            "headers": headers,
            "rowcount": numrows,
            "filename": filename,
        }
        haxdb.trigger("API.{}.CSV".format(self.API_NAME), event_data)

        return haxdb.func("FILE_DOWNLOAD")(filename, filedata, "text/csv")

    def list_call(self, table=None, params=None,
                  row_func=None, meta=None,
                  output_format=None):

        table = table or self.API_NAME
        query = haxdb.get("query")

        params = params or ()
        params += (self.API_NAME, self.API_CONTEXT_ID)

        meta = meta or {}
        meta.update(self.get_meta("list"))
        meta["query"] = query

        sql = """
            SELECT HDB_LIST.*,
            U1.UDF_NAME AS HAXDB_UDF_NAME,
            U1D.UDF_DATA_VALUE AS HAXDB_UDF_DATA_VALUE
            FROM {} HDB_LIST
            LEFT OUTER JOIN UDF U1 ON
                    U1.UDF_CONTEXT=%s
                    AND U1.UDF_CONTEXT_ID=%s
                    AND U1.UDF_ENABLED=1
            LEFT OUTER JOIN UDF_DATA U1D ON
                    U1D.UDF_DATA_UDF_ID=U1.UDF_ID
                    AND U1D.UDF_DATA_ROWID=HDB_LIST.{}
            WHERE
            1=1
            """.format(table, self.API_ROWID)

        rowid = haxdb.get("rowid")
        if rowid:
            sql += """
                AND {} = {}
            """.format(self.API_ROWID, rowid)
        else:
            rowid = haxdb.getlist("rowid")
            if rowid:
                try:
                    rowid = list(rowid)
                    rowid = map(int, rowid)
                    rowids = ",".join(str(x) for x in rowid)
                    sql += """
                        AND {} in ({})
                        """.format(self.API_ROWID, rowids)
                except (ValueError, TypeError) as e:
                    pass

        query_sql, query_params = self.build_query(query)
        sql += query_sql
        params += query_params

        sql += " GROUP BY HDB_LIST.{}, HAXDB_UDF_NAME".format(self.API_ROWID)
        if len(self.ORDER) > 0:
            sql += " ORDER BY {}, {}".format(",".join(self.ORDER),
                                             self.API_ROWID)
        else:
            sql += " ORDER BY {}".format(self.API_ROWID)

        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        rows = []
        rowdata = None
        lastrowid = None
        while row:
            row = dict(row)
            if row_func:
                row = row_func(dict(row))

            rowid = row[self.API_ROWID]
            if rowid != lastrowid:
                if rowdata:
                    rows.append(rowdata)
                rowdata = {}
                lastrowid = rowid
            if row["HAXDB_UDF_NAME"]:
                rowdata[row["HAXDB_UDF_NAME"]] = row["HAXDB_UDF_DATA_VALUE"]
            del row["HAXDB_UDF_NAME"]
            del row["HAXDB_UDF_DATA_VALUE"]
            rowdata.update(row)

            row = db.next()

        if rowdata:
            rows.append(rowdata)

        if output_format == "CSV":
            return self.csv_out(rows)

        event_data = {
            "api": self.API_NAME,
            "call": "list",
            "rowcount": len(rows),
        }
        haxdb.trigger("API.{}.LIST".format(self.API_NAME), event_data)

        return output(success=1, data=rows, meta=meta)

    def view_call(self, table=None, where=None,
                  params=None, row_func=None,
                  rowid=None, meta=None):
        rowid = rowid or haxdb.get("rowid")

        table = table or self.API_NAME
        where = where or "1=1"
        params = params or ()

        meta = meta or {}
        meta.update(self.get_meta("view"))
        meta["rowid"] = rowid

        sql = """
            select HAXDB_VIEW_TABLE.*
            FROM {} HAXDB_VIEW_TABLE
            WHERE
            {}
            and {}=%s
        """.format(table, where, self.API_ROWID)
        params += (rowid,)

        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)

        if not row:
            return output(success=0, meta=meta, message="NO DATA")

        row = dict(row)
        udf_sql = """
        SELECT * FROM UDF
        JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
        WHERE
        UDF_CONTEXT=%s and UDF_CONTEXT_ID=%s AND UDF_DATA_ROWID=%s
        AND UDF_ENABLED=1
        ORDER BY UDF_ORDER
        """
        udf_params = (self.API_NAME, self.API_CONTEXT_ID, rowid)
        db.query(udf_sql, udf_params)
        udf = db.next()
        while udf:
            row[udf["UDF_NAME"]] = udf["UDF_DATA_VALUE"]
            udf = db.next()

        if row_func:
            row = row_func(dict(row))

        event_data = {
            "api": self.API_NAME,
            "call": "view",
            "rowid": rowid,
        }
        if "ROW_NAME" in row:
            event_data["name"] = row["ROW_NAME"]
        haxdb.trigger("API.{}.VIEW".format(self.API_NAME), event_data)

        return output(success=1, meta=meta, data=row)

    def new_call(self, table=None, meta=None, defaults=None):
        defaults = defaults or {}
        table = table or self.API_NAME

        meta = meta or {}
        meta.update(self.get_meta("new"))

        col_names = []
        col_params = ()
        udf_names = []
        udf_params = []
        cols = self.get_cols()

        errors = ""
        for col in cols:
            val = haxdb.get(col["NAME"])
            if val is not None:
                if valid_value(col, val):
                    if col["NAME"] in self._COLS:
                        col_names.append(col["NAME"])
                        col_params += (val,)
                    else:
                        udf_names.append(col["NAME"])
                        udf_params.append(val)
                else:
                    errors += "INVALID VALUE FOR {}\n".format(col["NAME"])
            elif col["NAME"] in defaults:
                col_names.append(col["NAME"])
                col_params += (defaults[col["NAME"]],)
            elif col["REQUIRED"] == 1:
                errors += "{} IS REQUIRED.\n".format(col["NAME"])

        if errors:
            return output(success=0, meta=meta, message=errors)

        sql = """
        INSERT INTO {} ({})
        VALUES ({})
        """.format(table,
                   ",".join(col_names), ",".join(("%s",)*len(col_names)))
        db.query(sql, col_params)

        if db.error:
            return output(success=0, meta=meta, message=db.error)

        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            meta["rowid"] = db.lastrowid
            if udf_names:
                sql = """
                DELETE FROM UDF
                WHERE UDF_CONTEXT=%s
                AND UDF_CONTEXT_ID=%s
                and UDF_ROWID=%s
                """
                db.query(sql, (self.API_NAME,
                               self.API_CONTEXT_ID,
                               meta["rowid"]))
                for udf_key in udf_names.keys():
                    udf_name = udf_names[udf_key]
                    udf_val = udf_params[udf_key]
                    sql = """
                    INSERT INTO UDF
                    (UDF_CONTEXT, UDF_CONTEXT_ID, UDF_NAME, UDF_ROWID)
                    VALUES (%s, %s, %s, %s)
                    """
                    db.query(sql, (self.API_NAME,
                                   self.API_CONTEXT_ID,
                                   udf_name,
                                   udf_val))
                    if db.error:
                        return output(success=0, meta=meta, message=db.error)
            db.commit()

            event_data = {
                "api": self.API_NAME,
                "call": "new",
                "rowcount": meta["rowcount"],
                "rowid": meta["rowid"]
            }
            haxdb.trigger("API.{}.NEW".format(self.API_NAME), event_data)

            return output(success=1,
                          meta=meta,
                          message="{} ROWS CREATED".format(meta["rowcount"]),
                          value=db.lastrowid)

        return output(success=0, meta=meta, message="NO ROWS CREATED")

    def delete_call(self, table=None, sql=None, params=None,
                    meta=None, rowid=None):
        table = table or self.API_NAME
        meta = meta or {}
        meta.update(self.get_meta("delete"))
        meta["rowid"] = rowid

        udf_sql = """
            DELETE
            FROM UDF_DATA
            WHERE
            UDF_DATA_ROWID=%s
            AND UDF_DATA_UDF_ID IN
            (
            SELECT UDF_ID
            FROM UDF
            WHERE
            UDF_CONTEXT=%s
            AND UDF_CONTEXT_ID=%s
            )
        """
        db.query(udf_sql, (rowid, self.API_NAME, self.API_CONTEXT_ID))
        if db.error:
            return output(success=0, meta=meta, message=db.error)

        if not sql:
            rowid = rowid or haxdb.get("rowid")
            sql = "DELETE FROM {} WHERE {}=%s".format(table, self.API_ROWID)
            params = (rowid,)

        db.query(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)

        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            db.commit()
            event_data = {
                "api": self.API_NAME,
                "call": "delete",
                "rowcount": meta["rowcount"],
                "rowid": rowid,
            }
            haxdb.trigger("API.{}.DELETE".format(self.API_NAME), event_data)
            return output(success=1, meta=meta, message="DELETED")

        return output(success=0, meta=meta, message="NO ROWS DELETED")

    def save_call(self, table=None, meta=None, rowid=None):
        rowid = rowid or haxdb.get("rowid")
        table = table or self.API_NAME

        meta = meta or {}
        meta.update(self.get_meta("save"))
        meta["rowid"] = rowid

        if "updated" not in meta:
            meta["updated"] = []

        if "savedata" not in meta:
            meta["savedata"] = {}

        if "rowcount" not in meta:
            meta["rowcount"] = 0

        col_names = []
        col_params = ()
        udf_cols = []
        udf_params = []
        cols = self.get_cols()

        errors = ""
        saves = {}
        for col in cols:
            val = haxdb.get(col["NAME"])
            if val is not None:
                if "EDIT" in col and col["EDIT"] != 1:
                    errors += "{} IS NOT EDITABLE".format(col["NAME"])
                else:
                    if col["TYPE"] == "FILE":
                        sql = """
                            DELETE FROM FILES WHERE
                            FILES_CONTEXT=%s
                            AND FILES_CONTEXT_ID=%s
                            AND FILES_ROWID=%s
                        """
                        db.query(sql, (self.API_NAME,
                                       self.API_CONTEXT_ID,
                                       rowid))
                    if valid_value(col, val):
                        if col["NAME"] in self._COLS:
                            meta["savedata"][col["NAME"]] = val
                            meta["updated"].append(col["NAME"])
                            if val:
                                col_names.append("{}=%s".format(col["NAME"]))
                                col_params += (val,)
                            else:
                                col_names.append("{}=NULL".format(col["NAME"]))
                        else:
                            meta["updated"].append(col["NAME"])
                            udf_cols.append(col)
                            udf_params.append(val)
                    else:
                        errors += "INVALID VALUE FOR {}\n".format(col["NAME"])

        if errors:
            return output(success=0, meta=meta, message=errors)

        if col_names:
            sql = """
            UPDATE {} SET {} WHERE {}=%s
            """.format(table, ",".join(col_names), self.API_ROWID)
            col_params += (rowid,)
            db.query(sql, col_params)
            if db.error:
                return output(success=0, meta=meta, message=db.error)
            meta["rowcount"] = db.rowcount

        if udf_cols:
            for idx, udf_col in enumerate(udf_cols):
                udf_val = udf_params[idx]
                sql = """
                DELETE FROM UDF_DATA
                WHERE UDF_DATA_UDF_ID=%s and UDF_DATA_ROWID=%s
                """
                db.query(sql, (udf_col["UDF_ID"], rowid))
                if udf_val:
                    sql = """
                    INSERT INTO UDF_DATA
                    (UDF_DATA_UDF_ID, UDF_DATA_VALUE, UDF_DATA_ROWID)
                    VALUES (%s, %s, %s)
                    """
                    db.query(sql, (udf_col["UDF_ID"], udf_val, rowid))
                    if db.error:
                        return output(success=0, meta=meta, message=db.error)
                meta["rowcount"] = meta["rowcount"] or db.rowcount

        if meta["rowcount"] > 0:
            db.commit()
            event_data = {
                "api": self.API_NAME,
                "call": "save",
                "values": meta["savedata"],
                "rowcount": meta["rowcount"],
                "rowid": rowid,
            }
            haxdb.trigger("API.{}.SAVE".format(self.API_NAME), event_data)

            return output(success=1, meta=meta, message="SAVED")

        return output(success=0, meta=meta, message="NOTHING UPDATED")

    def download_call(self, rowid=None, field_name=None):
        rowid = rowid or haxdb.get("rowid")
        field_name = field_name or haxdb.get("field_name")

        sql = """
            SELECT * FROM FILES
            WHERE FILES_CONTEXT=%s
            AND FILES_CONTEXT_ID=%s
            AND FILES_FIELD_NAME=%s
            AND FILES_ROWID=%s
        """
        row = db.qaf(sql, (self.API_NAME, self.API_CONTEXT_ID,
                           field_name, rowid))
        if not row:
            msg = "UNKNOWN FIELD: {}".format(field_name)
            return output(success=0, message=msg)

        filedata = db._FROMBLOB(row["FILES_DATA"])
        ext = row["FILES_EXT"]
        filename = "{}.{}{}".format(self.API_NAME, field_name, ext)
        mimetype = row["FILES_MIMETYPE"]

        event_data = {
            "api": self.API_NAME,
            "call": "download",
            "field_name": field_name,
            "rowid": rowid,
            "filename": filename
        }
        haxdb.trigger("API.{}.DOWNLOAD".format(self.API_NAME), event_data)

        download = haxdb.get("download")
        if download and download == "dataurl":
            meta = self.get_meta("download")
            data = haxdb.func("FILE_DATAURL")(filedata, mimetype)
            return haxdb.output(success=1, meta=meta, data=data)

        return haxdb.func("FILE_DOWNLOAD")(filename, filedata, mimetype)

    def upload_call(self, table=None, rowid=None, field_name=None):
        rowid = rowid or haxdb.get("rowid")
        table = table or self.API_NAME
        field_name = field_name or haxdb.get("field_name")
        cols = self.get_cols()

        found = False
        for col in cols:
            if col["NAME"] == field_name:
                found = True
                break

        if not found:
            msg = "UNKNOWN FIELD: {}".format(field_name)
            return output(success=0, message=msg)

        if "file" not in request.files:
            return output(success=0, message="NO FILE UPLOADED")

        file = request.files["file"]
        if file.filename == '':
            return output(success=0, message="NOTHING UPDATED")

        fext = os.path.splitext(file.filename)[1]
        filedata = file.read()
        file.close()

        sql = """
            DELETE FROM FILES
            WHERE FILES_CONTEXT=%s
            AND FILES_CONTEXT_ID=%s
            AND FILES_FIELD_NAME=%s
            AND FILES_ROWID=%s
        """
        db.query(sql, (self.API_NAME, self.API_CONTEXT_ID, field_name, rowid))
        sql = """
            INSERT INTO FILES
            (FILES_CONTEXT, FILES_CONTEXT_ID, FILES_FIELD_NAME, FILES_MIMETYPE,
             FILES_ROWID, FILES_EXT, FILES_DATA)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        """
        db.query(sql, (self.API_NAME, self.API_CONTEXT_ID, field_name,
                       file.mimetype, rowid, fext, db._TOBLOB(filedata)))
        if db.error:
            return output(success=0, message=db.error)

        file_rowid = db.lastrowid

        if self.is_udf(col):
            sql = """
                DELETE FROM UDF_DATA
                WHERE
                UDF_DATA_ROWID=%s
                AND UDF_DATA_UDF_ID=%s
            """
            db.query(sql, (rowid, col["UDF_ID"]))
            sql = """
                INSERT INTO UDF_DATA
                (UDF_DATA_UDF_ID, UDF_DATA_ROWID, UDF_DATA_VALUE)
                VALUES (%s, %s, %s)
            """
            db.query(sql, (col["UDF_ID"], rowid, file_rowid))
        else:
            sql = """
                UPDATE {} SET {}=%s WHERE {}=%s
            """.format(table, field_name, self.API_ROWID)
            db.query(sql, (file_rowid, rowid))

        if db.error:
            return output(success=0, message=db.error)

        db.commit()

        event_data = {
            "api": self.API_NAME,
            "call": "upload",
            "field_name": field_name,
            "rowid": rowid,
        }
        haxdb.trigger("API.{}.UPLOAD".format(self.API_NAME), event_data)

        return output(success=1, message="FILE UPLOADED")

    def thumbnail_call(self, table=None, rowid=None):
        rowid = rowid or haxdb.get("rowid")
        table = table or self.API_NAME

        if not rowid:
            msg = "REQUIRED INPUT MISSING: rowid"
            return output(success=0, message=msg)

        f = None
        try:
            f = request.files["file"]
        except Exception as e:
            pass

        if f and f.filename and f.filename != '':
            # upload new thumbnail
            fext = os.path.splitext(f.filename)[1]
            filedata = f.read()
            thumb_big, thumb_small = haxdb.func("THUMBS_GEN")(file=f)
            f.close()

            if not thumb_big or not thumb_small:
                msg = "INVALID IMAGE FILE"
                return output(success=0, message=msg)
            sql = """
            DELETE FROM THUMBS WHERE THUMBS_TABLE=%s and THUMBS_ROWID=%s
            """
            db.query(sql, (table, rowid))

            sql = """
            INSERT INTO THUMBS
            (THUMBS_TABLE, THUMBS_ROWID, THUMBS_MIMETYPE, THUMBS_EXT,
            THUMBS_BIG, THUMBS_SMALL)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (table, rowid, "image/png", ".PNG",
                      db._TOBLOB(thumb_big), db._TOBLOB(thumb_small))
            db.query(sql, params)

            if db.error:
                return output(success=0, message=db.error)

            db.commit()

            event_data = {
                "api": self.API_NAME,
                "call": "thumbnail",
                "action": "upload",
                "table": table,
                "rowid": rowid,
            }
            tname = "API.{}.THUMBNAIL.UPLOAD".format(self.API_NAME)
            haxdb.trigger(tname, event_data)

            meta = self.get_meta("thumbnail")
            meta["rowid"] = rowid
            return output(success=1, meta=meta, message="THUMBNAIL UPLOADED")

        else:
            # download thumbnail
            size = haxdb.get("size")
            download = haxdb.get("download")

            sql = """
            SELECT * FROM THUMBS WHERE THUMBS_TABLE=%s AND THUMBS_ROWID=%s
            """
            row = db.qaf(sql, (table, rowid))
            if not row:
                msg = "NO THUMBNAIL"
                return output(success=0, message=msg)

            if size and size.lower() == "big":
                filedata = db._FROMBLOB(row["THUMBS_BIG"])
            else:
                filedata = db._FROMBLOB(row["THUMBS_SMALL"])

            filename = "{}.{}{}".format(table, rowid, row["THUMBS_EXT"])
            mimetype = row["THUMBS_MIMETYPE"]

            event_data = {
                "api": self.API_NAME,
                "call": "thumbnail",
                "download": download,
                "rowid": rowid,
                "filename": filename,
                "mimetype": mimetype
            }
            e = "API.{}.THUMBNAIL.DOWNLOAD".format(self.API_NAME)
            haxdb.trigger(e, event_data)

            download = haxdb.get("download")
            if download and download == "dataurl":
                meta = self.get_meta("thumbnail")
                meta["rowid"] = rowid
                value = haxdb.func("FILE_DATAURL")(filedata, mimetype)
                return haxdb.output(success=1, meta=meta, value=value)

            f = haxdb.func("FILE_DOWNLOAD")
            return f(filename, filedata, mimetype)
