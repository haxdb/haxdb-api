import os
import sys
from ConfigParser import ConfigParser
from os.path import join, isfile
import glob
import re

mods = {}
config = None
haxdb = None
db = None


def init(hdb, app_api):
    global config, haxdb, db, api
    haxdb = hdb
    config = haxdb.config
    db = haxdb.db
    api = app_api


def run():
    global mods, config, haxdb, db
    sys.path.insert(0, "coremods/")
    mod_names = []

    for name in glob.glob("coremods/*"):
        name = os.path.basename(name)
        if re.match(r'^\w+$', name):
            mod_names.append(name)

    db.open()

    for mod_name in mod_names:
        haxdb.logger.info("CORE: {}.init()".format(mod_name))
        mod_config = config.get("CORE_{}".format(mod_name.upper()), {})
        mod = __import__(mod_name)
        mod.init(haxdb, api, mod_config)
        mods[mod_name] = mod

    for mod in mods:
        haxdb.logger.info("{}.run()".format(mod))
        mods[mod].run()

    db.close()
