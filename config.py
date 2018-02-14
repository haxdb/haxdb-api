import os
from ConfigParser import ConfigParser
from os.path import join, isfile

CONFIG_FILE = join(os.getcwd(), 'haxdb.cfg')

if not isfile(CONFIG_FILE):
    raise Exception("I cannot open haxdb.cfg :(")

cfg = ConfigParser()
cfg.read(CONFIG_FILE)

config = {}

for section in cfg.sections():
    config[section] = {}
    for option in cfg.options(section):
        config[section.upper()][option.upper()] = cfg.get(section, option)
