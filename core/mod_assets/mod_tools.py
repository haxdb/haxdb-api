import time
import base64
import re
import os

haxdb = None
db = None
config = None


def init(app_config, app_db, app_haxdb):
    global haxdb, db, config
    haxdb = app_haxdb
    db = app_db
    config = app_config


def is_float(val):
    try:
        float(val)
        return True
    except:
        return False
