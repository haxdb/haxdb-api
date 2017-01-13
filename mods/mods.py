import os
import sys
from ConfigParser import ConfigParser
from os.path import join, isfile

mods = {}
config = None
haxdb = None
db = None


def read_mod_config(config_file):
    config = {
        "MOD": {
            "ENABLED": 1,
        }
    }
    if isfile(config_file):
        cfg = ConfigParser()
        cfg.read(config_file)
        for section in cfg.sections():
            config[section] = {}
            for option in cfg.options(section):
                config[section.upper()][option.upper()] = cfg.get(section, option)
    return config


def init(app_config, app_haxdb, app_db):
    global config, haxdb, db
    config = app_config
    haxdb = app_haxdb
    db = app_db


def run():
    global mods, config, haxdb, db
    sys.path.insert(0, config["MOD"]["PATH"])
    mod_names = [name for name in os.listdir(config["MOD"]["PATH"])
                 if os.path.isdir(os.path.join(config["MOD"]["PATH"], name))]

    db.open()

    for mod_name in mod_names:
        mod_config_file = os.path.join(config["MOD"]["PATH"], mod_name, "mod.cfg")
        mod_config = read_mod_config(mod_config_file)
        if int(mod_config["MOD"]["ENABLED"]) == 1:
            haxdb.logger.info("{}.init()".format(mod_name))
            mod = __import__(mod_name)
            mod.init(haxdb, mod_config)
            mods[mod_name] = mod
        else:
            haxdb.logger.info("{} DISABLED".format(mod_name))

    print ""

    for mod in mods:
        haxdb.logger.info("{}.run()".format(mod))
        mods[mod].run()
    print ""

    db.close()
