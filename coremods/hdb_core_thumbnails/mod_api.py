from flask import request

haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    @haxdb.route("/THUMBNAILS/getall", methods=haxdb.METHOD)
    def THUMBNAILS_get_all():
        context = haxdb.get("context")
        if not context:
            msg = "MISSING INPUT: context"
            return haxdb.response(success=0, message=msg)

        tfield = "THUMBNAILS_SMALL"
        if haxdb.get("big") == 1:
            tfield = "THUMBNAILS_BIG"

        sql = """
            SELECT THUMBNAILS_CONTEXTID, {}
            FROM THUMBNAILS
            WHERE THUMBNAILS_CONTEXT=%s
            """.format(tfield)
        r = haxdb.db.query(sql, (context,))

        if not r:
            msg = "NO THUMBNAIL"
            return haxdb.response(success=0, message=msg)

        data = {}
        for row in r:
            fdata = haxdb.db._FROMBLOB(row[tfield])
            fdata = haxdb.func("FILE:DATAURL")(fdata, "image/jpeg")
            data[row["THUMBNAILS_CONTEXTID"]] = fdata

        raw = {
            "data": data,
        }
        return haxdb.response(success=1, raw=raw)

    @haxdb.route("/THUMBNAILS/get", methods=haxdb.METHOD)
    def THUMBNAILS_get():
        context = haxdb.get("context")
        contextid = haxdb.get("contextid")

        if not context:
            msg = "MISSING INPUT: context"
            return haxdb.response(success=0, message=msg)

        if not contextid:
            msg = "MISSING INPUT: contextid"
            return haxdb.response(success=0, message=msg)

        tfield = "THUMBNAILS_SMALL"
        if haxdb.get("big") == 1:
            tfield = "THUMBNAILS_BIG"

        sql = """
            SELECT {}
            FROM THUMBNAILS
            WHERE THUMBNAILS_CONTEXT=%s
            AND THUMBNAILS_CONTEXTID=%s
            """.format(tfield)
        row = haxdb.db.qaf(sql, (context, contextid))

        if not row or not row[tfield]:
            msg = "NO THUMBNAIL"
            return haxdb.response(success=0, message=msg)

        fdata = haxdb.db._FROMBLOB(row[tfield])
        fdata = haxdb.func("FILE:DATAURL")(fdata, "image/jpeg")

        raw = {
            "data": fdata,
        }
        return haxdb.response(success=1, raw=raw)

    @haxdb.route("/THUMBNAILS/upload", methods=haxdb.METHOD)
    def THUMBNAILS_upload():
        context = haxdb.get("context")
        contextid = haxdb.get("contextid")

        if context not in haxdb.mod_def:
            msg = "UNKNOWN TABLE: {}".format(context)
            return haxdb.response(success=0, message=msg)

        mod = haxdb.mod_def[context]
        if not haxdb.func("PERM:HAS")(context, "WRITE", mod["AUTH"]["WRITE"]):
            msg = "INVALID PERMISSION"
            return haxdb.response(success=0, message=msg)

        try:
            f = request.files["upload"]
            f.read()
        except Exception:
            msg = "NO VALID FILE UPLOADED"
            return haxdb.response(success=0, message=msg)

        bthumb, sthumb = haxdb.func("THUMB:CREATE")(file=f)
        f.close()

        sql = """
            DELETE FROM THUMBNAILS
            WHERE THUMBNAILS_CONTEXT=%s
            AND THUMBNAILS_CONTEXTID=%s
            """
        haxdb.db.query(sql, (context, contextid))

        bthumb = haxdb.db._TOBLOB(bthumb)
        sthumb = haxdb.db._TOBLOB(sthumb)

        sql = """
            INSERT INTO THUMBNAILS (THUMBNAILS_CONTEXT, THUMBNAILS_CONTEXTID,
            THUMBNAILS_SMALL, THUMBNAILS_BIG)
            VALUES (%s, %s, %s, %s)
            """
        haxdb.db.query(sql, (context, contextid, sthumb, bthumb))

        haxdb.db.commit()
        return haxdb.response(success=1)
