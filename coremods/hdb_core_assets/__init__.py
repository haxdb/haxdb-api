import mod_api
from mod_def import mod_def

haxdb = None

def init(hdb):
    global haxdb
    haxdb = hdb
    haxdb.mod2db(mod_def)
    mod_api.init(haxdb)
    return mod_def


def run():
    haxdb.func("LISTS:CREATE")("ASSET_LOCATIONS", internal=True)
    mod_api.run()
