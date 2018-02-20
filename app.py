#! /usr/bin/env python

import logging
from config import config
import db
import haxdb
import haxdb_api
import haxdb_mods

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gunicorn.error")

haxdb.init(config, db.db(config["DB"], logger), haxdb_api, logger)
haxdb_api.init(haxdb)
haxdb_mods.init(haxdb)
haxdb_mods.run()

app = haxdb.flask_app
if __name__ == "__main__":
    haxdb.run()
else:
    haxdb.service()
