from flask import make_response
import base64

haxdb = None


def file_dataurl(filedata, mimetype):
    return "data:{};base64,{}".format(mimetype, base64.b64encode(filedata))


def file_download(filename, filedata, mimetype=None):
    r = make_response(filedata)
    cd = "attachment; filename={}".format(filename)
    r.headers["Content-Disposition"] = cd
    if mimetype:
        r.headers["Content-Type"] = mimetype

    event_data = {}
    event_data["filename"] = filename
    event_data["mimetype"] = mimetype
    haxdb.trigger("FILE:DOWNLOAD", event_data)

    return r


def file_csv(filename, headers, rows):
    import csv
    from datetime import datetime
    from StringIO import StringIO

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

    event_data = {}
    event_data["headers"] = headers
    event_data["rowcount"] = numrows
    event_data["filename"] = filename
    haxdb.trigger("FILE:DOWNLOAD:CSV", event_data)

    return file_download(filename, filedata, "text/csv")


def build_table_filelist(table, rowid=None):
    flist = {}
    print table
    if table not in haxdb.mod_def:
        return flist

    for col in haxdb.mod_def[table]["COLS"]:
        if col["TYPE"] == "FILE":
            flist[col["NAME"]] = []

    sql = "SELECT FILES_COLUMN, FILES_ROWID FROM FILES WHERE FILES_TABLE=%s"
    params = (table,)

    if rowid:
        sql += " AND FILES_ROWID=%s"
        params += (rowid,)

    r = haxdb.db.query(sql, params)
    if not r:
        return flist
    for row in r:
        if row["FILES_COLUMN"] in flist:
            flist[row["FILES_COLUMN"]].append(row["FILES_ROWID"])

    return flist


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("FILE:DOWNLOAD", file_download)
    haxdb.func("FILE:CSV", file_csv)
    haxdb.func("FILE:DATAURL", file_dataurl)
    haxdb.func("FILE:TABLE:BUILD", build_table_filelist)


def run():
    pass
