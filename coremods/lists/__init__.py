import mod_func
import mod_api
from mod_def import mod_def


def init(haxdb):
    haxdb.mod2db(mod_def)
    mod_func.init(haxdb)
    mod_api.init(haxdb)


def run():
    mod_func.run()
    mod_api.run()
