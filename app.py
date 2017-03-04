#!/usr/bin/python

import logging
from config import config
import db
import haxdb
import core

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config, db.db(config["DB"], logger), logger)

core.init(haxdb)
core.run()

try:
    import mods
    mods.init(haxdb)
    mods.run()
except ImportError:
    pass

app = haxdb.app


if __name__ == "__main__":
    haxdb.run()
