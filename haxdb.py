from functools import wraps
from flask import Flask, session
import os, time, shlex
from datetime import timedelta
from flask_cors import CORS
import data
import api

app = Flask("hdbapi")
app.secret_key = os.urandom(24)

VERSION = "v1"
config = None
db = None
logger = None

def init(app_config, app_db, app_logger):
    global config, db, api, logger
    config = app_config
    db = app_db
    logger = app_logger
    api.init(db)

def run():
    debug = (int(config["DEBUG"]) == 1)
    CORS(app, origin=config["ORIGINS"])
    app.permanent_session_lifetime = timedelta(seconds=int(config["SESSION_TIMEOUT"]))
    app.run(config["HOST"],int(config["PORT"]), debug=debug)
    

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
        key = data.session.get("api_key")
        authenticated = data.session.get("api_authenticated")

        if not (key and authenticated==1):
            return data.output(success=0, message="NOT AUTHENTICATED", authenticated=False)
        return view_function(*args, **kwargs)

    return decorated_function

def require_dba(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        session.permanent = True
        dba = data.session.get("api_dba")
        if (not dba or (dba and int(dba) != 1)):
            return data.output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


def no_readonly(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        session.permanent = True
        readonly = data.session.get("api_readonly")

        if (readonly and readonly==1):
            return data.output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


