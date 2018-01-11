import mod_api
from mod_def import mod_def


def init(haxdb):
    haxdb.mod2db(mod_def)
    mod_api.init(haxdb)
    return {}


def run():
    mod_api.run()
