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
    return r


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb


def run():
    haxdb.save_function("FILE_DOWNLOAD", file_download)
    haxdb.save_function("FILE_DATAURL", file_dataurl)
