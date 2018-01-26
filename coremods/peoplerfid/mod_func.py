import base64

haxdb = None


def rfid_create():
    size = haxdb.config["RFID"]["SIZE"]
    return base64.urlsafe_b64encode(os.urandom(500))[5:5+size]


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb


def run():
    haxdb.func("RFID:CREATE", rfid_create)
