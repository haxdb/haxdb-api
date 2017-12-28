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

    if col_type in ("TEXT", "STR", "LIST", "ASCII"):
        return True

    if col_type == "DATE":
        r = "^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$"
        d = re.compile(r)
        return d.match(val)


def build_query(self, query):
    pass


def get_udf(table):
    pass


def list_call(mod_def):
    table = mod_def["TABLE"]
    query = haxdb.get("query")
    csv = haxdb.get("csv")

    udf = get_udf(table)


    if csv == 1:
        return haxdb.func("FILE_CSV")(filename, headers, rows)

    event_data = {
        "api": self.API_NAME,
        "call": "list",
        "rowcount": len(rows),
    }
    haxdb.trigger("API.{}.LIST".format(self.API_NAME), event_data)

    return output(success=1, data=rows, meta=meta)


def view_call(mod_def, rowid=None):
    rowid = rowid or haxdb.get("rowid")

    table = mod_def["TABLE"]
    row_id = "{}_ID".format(table)
    row_name = mod_def["ROW_NAME"]

    sql = """
            select
                {} AS ROW_ID,
                {} AS ROW_NAME,
                HVT.*
            FROM {} HVT
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
