import base64

haxdb = None

def apikey_create():
    size = haxdb.config["NODES"]["APIKEY_SIZE"]
    return base64.urlsafe_b64encode(os.urandom(500))[5:5+size]


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("APIKEY_CREATE", apikey_create)


def run():
    pass
