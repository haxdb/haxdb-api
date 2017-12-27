from functools import wraps
from flask import Flask, session as sess, jsonify, json, request
import msgpack
import os
import time
from datetime import timedelta
from flask_cors import CORS
import haxdb_data
import haxdb_api as api
import re

app = Flask("haxdb-api")
app.secret_key = os.urandom(24)

VERSION = "v1"
config = None
db = None
logger = None
saved_functions = {}
saved_triggers = []


class error:
    message = ""

    def __init__(self, msg):
        self.message = msg

    def __bool__(self):
        return False
    __nonzero__ = __bool__

    def __repr__(self):
        return self.message
    __str__ = __repr__


def get(key, use_session=False):
    r = haxdb_data.var.getlist(key)
    if isinstance(r, list):
        return r
    return haxdb_data.var.get(key, use_session)


def session(key, val=None):
    if val:
        haxdb_data.session.set(key, val)
    else:
        return haxdb_data.session.get(key)


def response(success=0, message=None, data=None, raw=None):
    output_format = get("format")

    out = raw or {}
    out["success"] = success
    out["value"] = value
    out["message"] = message
    out["timestamp"] = time.time()
    out["authenticated"] = 1 if authenticated else 0
    out["data"] = None if not data else data

    if output_format and output_format == "msgpack":
        return msgpack.packb(out)

    return json.dumps(out)


def func(name, f=None):
    if f:
        saved_functions[name] = f
    elif name in saved_functions:
        return saved_functions[name]
    return None


def on(event_regex, func):
    e = re.compile(event_regex, re.IGNORECASE)
    trigger = (e, func)
    saved_triggers.append(trigger)


def trigger(event, data):
    data["EVENT"] = event
    data["NODES_ID"] = session("nodes_id") or 0
    data["NODES_NAME"] = session("nodes_name") or ''
    logger.debug("TRIGGER: {}: {}".format(event, data))
    for trigger in saved_triggers:
        e = trigger[0]
        if e.search(event):
            f = trigger[1]
            try:
                f(data)
            except TypeError:
                msg = "INVALID TRIGGER FUNCTION FOR: {} ".format(event)
                logger.error(msg)


def init(app_config, app_db, app_logger):
    global config, db, api, logger
    config = app_config
    db = app_db
    logger = app_logger


def run():
    debug = (int(config["API"]["DEBUG"]) == 1)
    CORS(app, origin=config["API"]["ORIGINS"])
    timeout = config["API"]["SESSION_TIMEOUT"]
    app.permanent_session_lifetime = timedelta(seconds=int(timeout))
    app.run(config["API"]["HOST"], int(config["API"]["PORT"]), debug=debug)


@app.before_request
def open_db():
    db.open()


@app.teardown_appcontext
def close_db(error):
    db.close()


def require_auth(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        session.permanent = True
        key = haxdb_data.session.get("api_key")
        authenticated = haxdb_data.session.get("api_authenticated")

        if not (key and authenticated == 1):
            msg = "NOT AUTHENTICATED"
            return output(success=0, message=msg, authenticated=False)
        return view_function(*args, **kwargs)

    return decorated_function


def require_dba(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        session.permanent = True
        dba = haxdb_data.session.get("api_dba")
        if (not dba or (dba and int(dba) != 1)):
            return output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


def no_readonly(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        session.permanent = True
        readonly = haxdb_data.session.get("api_readonly")

        if (readonly and readonly == 1):
            return output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function
