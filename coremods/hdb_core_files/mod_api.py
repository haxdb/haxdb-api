import os
from mod_def import mod_def
from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    @haxdb.route("/FILES/clear", methods=haxdb.METHOD)
    def FILES_clear():
        context = haxdb.get("context")
        subcontext = haxdb.get("subcontext")
        contextid = haxdb.get("contextid")

        col = haxdb.func("META:COL:GET")(context, subcontext)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(subcontext)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(context, "WRITE", col["AUTH"]["WRITE"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            DELETE FROM FILES
            WHERE FILES_CONTEXT=%s
            AND FILES_SUBCONTEXT=%s
            AND FILES_CONTEXTID=%s
            """
        haxdb.db.query(sql, (context, subcontext, contextid))
        haxdb.db.commit()

        raw = {
            "context": context,
            "subcontext": subcontext,
            "contextid": contextid,
        }
        return haxdb.response(success=1, message="FILE CLEARED", raw=raw)

    @haxdb.route("/FILES/upload", methods=haxdb.METHOD)
    def FILES_upload():
        context = haxdb.get("context")
        contextid = haxdb.get("contextid")
        subcontext = haxdb.get("subcontext")

        print context, contextid, subcontext
        col = haxdb.func("META:COL:GET")(context, subcontext)

        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD"
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(context, "WRITE", col["AUTH"]["WRITE"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        if "upload" not in request.files:
            msg = "NO FILE UPLOADED"
            return haxdb.response(success=0, message=msg)

        f = request.files["upload"]
        if not f.filename or f.filename == '':
            msg = "NO FILE UPLOADED"
            return haxdb.response(success=0, message=msg)

        fext = os.path.splitext(f.filename)[1][1:]
        fmime = f.mimetype
        fdata = haxdb.db._TOBLOB(f.read())
        f.close()

        sql = """
            DELETE FROM FILES
            WHERE FILES_CONTEXT=%s
            AND FILES_SUBCONTEXT=%s
            AND FILES_CONTEXTID=%s
            """
        haxdb.db.query(sql, (context, subcontext, contextid))

        sql = """
            INSERT INTO FILES
            (FILES_CONTEXT, FILES_SUBCONTEXT, FILES_CONTEXTID,
            FILES_EXT, FILES_MIMETYPE, FILES_DATA)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        params = (context, subcontext, contextid, fext, fmime, fdata)
        haxdb.db.query(sql, params)
        if haxdb.db.error:
            haxdb.db.rollback()
            return haxdb.response(success=0, message=haxdb.db.error)
        haxdb.db.commit()

        raw = {
            "api": context,
            "subcontext": subcontext,
            "contextid": contextid,
        }
        return haxdb.response(success=1, message="FILE SAVED", raw=raw)

    @haxdb.route("/FILES/download", methods=haxdb.METHOD)
    def FILES_download():
        context = haxdb.get("context")
        subcontext = haxdb.get("subcontext")
        contextid = haxdb.get("contextid")

        col = haxdb.func("META:COL:GET")(context, subcontext)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(subcontext)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(context, "READ", col["AUTH"]["READ"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            SELECT * FROM FILES
            WHERE FILES_CONTEXT=%s
            AND FILES_SUBCONTEXT=%s
            AND FILES_CONTEXTID=%s
        """
        row = haxdb.db.qaf(sql, (context, subcontext, contextid))
        if not row:
            msg = "NO FILE"
            return haxdb.response(success=0, message=msg)

        ext = row["FILES_EXT"]
        mimetype = row["FILES_MIMETYPE"]
        filedata = haxdb.db._FROMBLOB(row["FILES_DATA"])
        filename = "{}.{}.{}{}".format(context, subcontext, contextid, ext)

        return haxdb.func("FILE:DOWNLOAD")(filename, filedata, mimetype)

    @haxdb.route("/FILES/get", methods=haxdb.METHOD)
    def FILES_get():
        context = haxdb.get("context")
        subcontext = haxdb.get("subcontext")
        contextid = haxdb.get("contextid")

        col = haxdb.func("META:COL:GET")(context, subcontext)
        if not col or col["TYPE"] != "FILE":
            msg = "INVALID FIELD: {}".format(subcontext)
            return haxdb.response(success=0, message=msg)

        if not haxdb.func("PERM:HAS")(context, "READ", col["AUTH"]["READ"]):
            msg = "INVALID PERMISSIONS"
            return haxdb.response(success=0, message=msg)

        sql = """
            SELECT * FROM FILES
            WHERE
            FILES_CONTEXT=%s AND FILES_SUBCONTEXT=%s AND FILES_CONTEXTID=%s
        """
        row = haxdb.db.qaf(sql, (context, subcontext, contextid))
        if not row:
            msg = "NO FILE"
            return haxdb.response(success=0, message=msg)

        ext = row["FILES_EXT"]
        mimetype = row["FILES_MIMETYPE"]
        filedata = haxdb.func("FILE:DATAURL")(row["FILES_DATA"], mimetype)
        filename = "{}.{}.{}.{}".format(context, subcontext, contextid, ext)
        raw = {
            "api": context,
            "subcontext": subcontext,
            "contextid": contextid,
            "filename": filename,
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
