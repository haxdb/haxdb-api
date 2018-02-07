haxdb = None


def get_col(mod_name, col_name):
    if mod_name not in haxdb.mod_def:
        return False

    for col in haxdb.mod_def[mod_name]:
        if col["NAME"] == col_name:
            return col
    return False


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("META:COL:GET", get_col)

def run():
    pass
