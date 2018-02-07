import mod_api
import mod_func


def init(haxdb):
    mod_func.init(haxdb)
    mod_api.init(haxdb)
    return {}


def run():
    mod_func.run()
    mod_api.run()
