import os
import sys
from ConfigParser import ConfigParser
from os.path import join, isfile
import glob

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
    print config_file,
    if isfile(config_file):
        print "FOUND"
        cfg = ConfigParser()
        cfg.read(config_file)
        for section in cfg.sections():
            config[section] = {}
            for option in cfg.options(section):
                config[section.upper()][option.upper()] = cfg.get(section,
                                                                  option)
    else:
        print "NO"
    return config


def init(hdb):
    global config, haxdb, db
    haxdb = hdb
    config = haxdb.config
    db = haxdb.db


def run():
    global mods, config, haxdb, db
    sys.path.insert(0, config["CORE"]["PATH"])
    modpattern = "{}/haxdb_*".format(config["CORE"]["PATH"])
    mod_names = []
    for name in glob.glob(modpattern):
        mod_names.append(os.path.basename(name))

    db.open()

    for mod_name in mod_names:
        mod_config_file = os.path.join(config["CORE"]["PATH"],
                                       mod_name,
                                       "mod.cfg")
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
