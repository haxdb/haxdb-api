import time
import base64
import re
import os


class tool_error:

    message = ""

    def __init__(self, msg):
        self.message = msg

    def __bool__(self):
        return False
    __nonzero__ = __bool__

    def __repr__(self):
        return self.message
    __str__ = __repr__


haxdb = None
db = None
config = None


def init(app_config, app_db, app_haxdb):
    global haxdb, db, config
    haxdb = app_haxdb
    db = app_db
    config = app_config
