import mod_api
from mod_def import mod_def
import mod_func

def init(haxdb):
    haxdb.mod2db(mod_def)
    mod_func.init(haxdb)
    mod_api.init(haxdb)
    return mod_def


def run():
    mod_func.run()
    mod_api.run()
