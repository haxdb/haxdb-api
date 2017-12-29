import mod_db
import mod_func

haxdb = None

def init(hdb):
    global haxdb
    haxdb = hdb
    haxdb.mod2db(mod_def)
    mod_func.init(haxdb)


def run():
    mod_func.run()
