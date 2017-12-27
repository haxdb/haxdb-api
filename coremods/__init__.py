import os
import sys
import glob
import re

mods = {}
haxdb = None


def init(hdb):
    global haxdb
    haxdb = hdb


def run():
    global mods, haxdb
    sys.path.insert(0, "coremods/")
    mod_names = []

    for name in glob.glob("coremods/*"):
        name = os.path.basename(name)
        if re.match(r'^\w+$', name):
            mod_names.append(name)

    db.open()

    for mod_name in mod_names:
        haxdb.logger.info("CORE: {}.init()".format(mod_name))
        mod = __import__(mod_name)
        mod.init(haxdb)
        mods[mod_name] = mod

    for mod in mods:
        haxdb.logger.info("{}.run()".format(mod))
        mods[mod].run()

    db.close()
