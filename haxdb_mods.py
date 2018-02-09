import os
import sys
import glob
import re
import imp

mods = {}
mod_defs = {}
haxdb = None


def import_mods(path):
    mod_names = []

    for name in glob.glob("{}/*".format(path)):
        name = os.path.basename(name)
        if re.match(r'^\w+$', name):
            mod_names.append(name)

    for mod_name in mod_names:
        mod_path = "{}/{}".format(path, mod_name)
        fp, path_name, description = imp.find_module(mod_name, [path, ])
        mods[mod_name] = imp.load_module(mod_name, fp, path_name, description)

    return mod_names


def init(hdb):
    global haxdb
    haxdb = hdb


def run():

    # usermods first so that coremods will overwrite.
    usermods = import_mods(haxdb.config["MODS"]["USER"])
    coremods = import_mods(haxdb.config["MODS"]["CORE"])
    mod_names = set(usermods + coremods)

    haxdb.db.open()

    haxdb.logger.info(" Initializing MODS:")
    for mod in mod_names:
        haxdb.logger.info("\t{}".format(mod))
        mod_def = mods[mod].init(haxdb)
        haxdb.mod_def.update(mod_def)

    haxdb.logger.info(" Running MODS:")
    for mod in mod_names:
        haxdb.logger.info("\t{}".format(mod))
        mods[mod].run()

    haxdb.db.close()
