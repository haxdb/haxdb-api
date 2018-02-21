from functools import wraps
from flask import Flask, session, json, request, Blueprint
from flask_cors import CORS
import msgpack
import os
import time
from datetime import timedelta
import re
# import haxdb_data

VERSION = "v1"
METHOD = ["POST", "GET"]

flask_app = Flask("haxdb-api")
flask_app.secret_key = os.urandom(24)
api_app = Blueprint(VERSION, "haxdb-api-version")
route = api_app.route

config = None
db = None
api = None
logger = None
saved_functions = {}
saved_triggers = []
mod_def = {}
user_data = None


class error(str):
    message = ""

    def __init__(self, msg):
        self.message = str(msg)

    def __bool__(self):
        return False
    __nonzero__ = __bool__

    def __repr__(self):
        return self.message
    __str__ = __repr__


def mod2db(mod_def):
    return db.mod2db(mod_def)


def get(key, use_session=False):
    global user_data
    if use_session:
        r = session.get(key, None)
        if r:
            return r

    if user_data is None:
        try:
            user_data = request.get_json() or {}
        except Exception:
            print "wat"
            user_data = {}
            return None

    val = user_data.get(key, None)
    if not val:
        val = request.form.get(key, None)
    if not val:
        val = request.args.get(key, None)

    return val


def response(success=None, message=None, raw=None):
    output_format = get("format")
    authenticated = session.get("authenticated", 0)

    out = raw or {}
    if success is not None:
        out["success"] = success
        out["authenticated"] = authenticated
    if "message" not in out:
        out["message"] = message
    out["timestamp"] = time.time()

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
    data["NODES_ID"] = session.get("nodes_id", 0)
    data["NODES_NAME"] = session.get("nodes_name", '')
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


def init(app_config, app_db, app_api, app_logger):
    global config, db, api, logger
    config = app_config
    db = app_db
    api = app_api
    logger = app_logger


def service():
    timeout = config["API"]["SESSION_TIMEOUT"]
    flask_app.permanent_session_lifetime = timedelta(seconds=int(timeout))
    flask_app.register_blueprint(api_app, url_prefix="/{}".format(VERSION))


def run():
    debug = (int(config["API"]["DEBUG"]) == 1)
    CORS(flask_app, origins=config["API"]["ORIGINS"])
    timeout = config["API"]["SESSION_TIMEOUT"]
    host = config["API"]["HOST"]
    port = int(config["API"]["PORT"])
    flask_app.permanent_session_lifetime = timedelta(seconds=int(timeout))
    flask_app.register_blueprint(api_app, url_prefix="/{}".format(VERSION))

    for rule in flask_app.url_map.iter_rules():
        print rule

    flask_app.run(host, port, debug=debug)


@flask_app.before_request
def open_db():
    global user_data
    db.open()
    user_data = None


@flask_app.teardown_appcontext
def close_db(error):
    db.close()


def require_dba(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        session.permanent = True
        dba = session.get("dba")
        if (not dba or (dba and int(dba) != 1)):
            return response(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function
