import mod_api
from mod_def import mod_def


def init(haxdb):
    mod_api.init(haxdb)
    haxdb.mod2db(mod_def)
    return mod_def


def run():
    mod_api.run()
