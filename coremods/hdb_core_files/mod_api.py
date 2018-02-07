from mod_def import mod_def
from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/FILES/clear", methods=haxdb.METHOD)
    def FILES_upload():
        mod = haxdb.get("mod")
        field = haxdb.get("field")
        rowid = haxdb.get("rowid")

        col = haxdb.func("META:COL:GET")(mod, field)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(field)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(mod, "WRITE", col["AUTH"]["WRITE"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            DELETE FROM FILES
            WHERE FILES_TABLE=%s AND FILES_COLUMN=%s and FILES_ROWID=%s
            """
        haxdb.db.query(sql, (mod, field, rowid))
        haxdb.db.commit()

        return haxdb.response(success=1, message="FILE CLEARED")


    @haxdb.route("/FILES/upload", methods=haxdb.METHOD)
    def FILES_upload():
        mod = haxdb.get("mod")
        rowid = haxdb.get("rowid")

        for field in request.files:
            col = haxdb.func("META:COL:GET")(mod, field)
            if not col or col["TYPE"] != "FILE":
                msg = "INVALID FIELD: {}".format(field)
                return haxdb.response(success=0, message=msg)

            if not haxdb.func("PERM:HAS")(mod, "WRITE", col["AUTH"]["WRITE"]):
                msg = "INVALID PERMISSIONS"
                return haxdb.response(success=0, message=msg)

            f = request.files[field]
            if not f.filename or file.filename == '':
                msg = "NO FILE UPLOADED"
                return haxdb.response(success=0, message=msg)

            fext = os.path.splitext(f.filename)[1]
            fmime = f.mimetype
            fdata = file.read()
            f.close()

            sql = """
                DELETE FROM FILES
                WHERE FILES_TABLE=%s AND FILES_COLUMN=%s and FILES_ROWID=%s
                """
            haxdb.db.query(sql, (mod, field, rowid))

            sql = """
                INSERT INTO FILES
                (FILES_TABLE, FILES_COLUMN, FILES_ROWID,
                FILES_EXT, FILES_MIMETYPE, FILES_DATA)
                VALUES (%s, %s, %s, %s, %s)
            """
            haxdb.db.query(mod, field, rowid, fext, fmime, fdata)
            if haxdb.db.error:
                haxdb.db.rollback()
                return haxdb.response(success=0, message=haxdb.db.error)
            haxdb.db.commit()

            raw = {
                "api": mod,
                "field": field,
                "rowid": rowid,
            }
            return haxdb.response(success=1, message="FILE SAVED", raw=raw)


    @haxdb.route("/FILES/download/<mod>/<field>/<rowid>", methods=haxdb.METHOD)
    @haxdb.route("/FILES/download", methods=haxdb.METHOD)
    def FILES_download(mod=None, field=None, rowid=None):
        mod = mod or haxdb.get("mod")
        field = field or haxdb.get("field")
        rowid = rowid or haxdb.get("rowid")

        col = haxdb.func("META:COL:GET")(mod, field)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(field)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(mod, "READ", col["AUTH"]["READ"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            SELECT * FROM FILES
            WHERE
            FILES_TABLE=%s AND FILES_COLUMN=%s AND FILES_ROWID=%s
        """
        row = haxdb.db.qaf(sql, mod, field, rowid)
        if not row:
            msg = "NO FILE"
            return haxdb.response(success=0, message=msg)

        ext = row["FILES_EXT"]
        mimetype = row["FILES_MIMETYPE"]
        filedata = row["FILES_DATA"]
        filename = "{}.{}.{}.{}".format(mod, field, rowid, ext)

        return haxdb.func("FILE:DOWNLOAD")(filename, filedata, mimetype)


    @haxdb.route("/FILES/get/<mod>/<field>/<rowid>", methods=haxdb.METHOD)
    @haxdb.route("/FILES/get", methods=haxdb.METHOD)
    def FILES_get(mod=None, field=None, rowid=None):
        mod = mod or haxdb.get("mod")
        field = field or haxdb.get("field")
        rowid = rowid or haxdb.get("rowid")

        col = haxdb.func("META:COL:GET")(mod, field)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(field)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(mod, "READ", col["AUTH"]["READ"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            SELECT * FROM FILES
            WHERE
            FILES_TABLE=%s AND FILES_COLUMN=%s AND FILES_ROWID=%s
        """
        row = haxdb.db.qaf(sql, mod, field, rowid)
        if not row:
            msg = "NO FILE"
            return haxdb.response(success=0, message=msg)

        ext = row["FILES_EXT"]
        mimetype = row["FILES_MIMETYPE"]
        filedata = haxdb.func("FILE:DATAURL")(row["FILES_DATA"], mimetype)
        raw = {
            "api": mod,
            "field": field,
            "rowid": rowid,
            "filename": "{}.{}.{}.{}".format(mod, field, rowid, ext),
            "mimetype": mimetype,
            "data": filedata,
        }
        return haxdb.response(success=1, raw=raw)

    @haxdb.route("/FILES/list", methods=haxdb.METHOD)
    def FILES_list():
        return haxdb.api.list_call(mod_def["FILES"])

    @haxdb.route("/FILES/view", methods=haxdb.METHOD)
    def FILES_view():
        return haxdb.api.view_call(mod_def["FILES"])

    @haxdb.route("/FILES/new", methods=haxdb.METHOD)
    def FILES_new():
        return haxdb.api.new_call(mod_def["FILES"])

    @haxdb.route("/FILES/delete", methods=haxdb.METHOD)
    def FILES_delete():
        return haxdb.api.delete_call(mod_def["FILES"])

    @haxdb.route("/FILES/save", methods=haxdb.METHOD)
    def FILES_save():
        return haxdb.api.save_call(mod_def["FILES"])
