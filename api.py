from functools import wraps
from flask import Flask
import os, time, shlex
from datetime import timedelta
from flask_cors import CORS
from data import *

app = Flask("hdbapi")
app.secret_key = os.urandom(24)

VERSION = "v1"
config = None
db = None

def run():
    debug = (int(config["DEBUG"]) == 1)
    CORS(app, origin=config["ORIGINS"])
    app.permanent_session_lifetime = timedelta(seconds=int(config["SESSION_TIMEOUT"]))
    app.run(config["HOST"],int(config["PORT"]), debug=debug)
    

def require_auth(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        key = session.get("api_key")
        authenticated = session.get("api_authenticated")

        if not (key and authenticated==1):
            return output(success=0, message="NOT AUTHENTICATED", authenticated=False)
        return view_function(*args, **kwargs)

    return decorated_function

def require_dba(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        dba = session.get("api_dba")
        if (not dba or (dba and int(dba) != 1)):
            return output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


def no_readonly(view_function):
    @wraps(view_function)
    
    def decorated_function(*args, **kwargs):
        sess.permanent = True
        readonly = session.get("api_readonly")

        if (readonly and readonly==1):
            return output(success=0, message="INVALID PERMISSION")
        return view_function(*args, **kwargs)

    return decorated_function


###################################################################################

def valid_value(col_type, val):
    if col_type == "BOOL" and val in (0,1,'0','1'):
        return True

    if col_type == "INT":
        try:
            int(val)
        except: 
            return False
        return True
    
    if col_type == "STR":
        return True
    
    return False

###################################################################################

def api_list (d, sql, query, query_cols, search_cols, order_cols, lists=None):
    include_lists = data.get("include_lists")
    d["input"]["include_lists"] = include_lists
    if include_lists and lists:
        d["lists"] = {}
        
        for list_name in lists:
            d["lists"][list_name] = []
            list_sql = """
            SELECT * FROM LIST_ITEMS 
            JOIN LISTS ON LISTS_ID = LIST_ITEMS_LISTS_ID AND LISTS_NAME=?
            WHERE
            LIST_ITEMS_ENABLED = '1'
            ORDER BY LIST_ITEMS_ORDER
            """
            db.query(list_sql, (list_name,))
            print db.error
            row = db.next()
            while row:
                d["lists"][list_name].append(dict(row))
                row = db.next()
                
    params = ()
    if query:
        queries = shlex.split(query)
        for query in queries:
            qs = query.split(":")
            if len(qs) > 1:
                col = qs[0]
                if col in query_cols:
                    vals = qs[1].split("|")
                    
                    sql += " AND ("
                    valcount = 0
                    for val in vals:
                        if valcount > 0:
                            sql += " OR "
                            
                        if val == "NULL":
                            sql += "%s IS NULL" % (col,)
                        else:
                            sql += "%s = ?" % (col,)
                            params += (val,)
                        
                        valcount += 1
                        
                    sql += ")"
            else:
                sql += " AND ("
                valcount = 0

                for col in search_cols:
                    if valcount > 0:
                        sql += " OR "
                    sql += " %s LIKE ? " % (col,)
                    params += (query,)
                    valcount += 1
                    
                sql += ")"
                
    if len(order_cols) > 0:
        sql += " ORDER BY %s" % ",".join(order_cols)
    
    
    db.query(sql,params)
    if db.error:
        print sql
        return output(success=0, data=d, message=db.error)

    row = db.next()
    rows = []
    while row:
        rows.append(dict(row))
        row = db.next()

    return output(success=1, data=d, rows=rows)
                
def api_view(d,sql,params, lists=None):
    include_lists = data.get("include_lists")
    d["input"]["include_lists"] = include_lists
    if include_lists and lists:
        d["lists"] = {}
        
        for list_name in lists:
            d["lists"][list_name] = []
            list_sql = """
            SELECT * FROM LIST_ITEMS 
            JOIN LISTS ON LISTS_ID = LIST_ITEMS_LISTS_ID AND LISTS_NAME=?
            WHERE
            LIST_ITEMS_ENABLED = '1'
            ORDER BY LIST_ITEMS_ORDER
            """
            db.query(list_sql, (list_name,))
            row = db.next()
            while row:
                d["lists"][list_name].append(dict(row))
                row = db.next()
                
                
    row = db.qaf(sql, params)
    if db.error:
        return output(success=0, data=d, message=db.error)
    
    if not row:
        return output(success=0, data=d, message="NO DATA")
    
    d["row"] = dict(row)
    return output(success=1, data=d)

def api_save(data,sql,params,col,val,valid_cols):
    if col not in valid_cols:
        return output(success=0, data=data, message="INVALID COL: %s" % (col,))
    
    col_type = valid_cols[col]
    if not valid_value(col_type, val):
        return output(success=0, data=data, message="INVALID %s VALUE FOR COL (%s): %s" % (col_type, col, val))
    
    sql = sql % (col,)
    db.query(sql, params)
    
    if db.error:
        return output(success=0, data=data, message=db.error)
    
    data["rowcount"] = db.rowcount
    if data["rowcount"] > 0:
        db.commit()
        return output(success=1, data=data, message="SAVED")
    else:
        return output(success=0, data=data, message="NO ROWS SAVED")
    