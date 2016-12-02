import os, base64, json, time, re
from flask import request

haxdb = None
db = None
config = None
tools = None

def init(app_haxdb, app_db, app_config, mod_tools):
    global haxdb, db, config, tools
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = mod_tools


def run():
    global haxdb, config, db, tools

    @haxdb.app.route("/AUTH/email/login", methods=["GET","POST"])
    @haxdb.app.route("/AUTH/email/login/<email>", methods=["GET","POST"])
    def mod_auth_email(email=None):
        email = email or haxdb.data.var.get("email")
        subject = haxdb.data.var.get("subject")
        message = haxdb.data.var.get("message")
        email = email.upper()
        
        meta = {}
        meta["api"] = "AUTH/email"
        meta["action"] = "login"
        meta["email"] = email
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return haxdb.data.output(success=0, message="INVALID VALUE: email", meta=meta)

        # EMAIL EXISTS?
        sql = "SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL = ?"
        people = db.qaf(sql, (email,))
        if not people:
            return haxdb.data.output(success=0, value=1, message="NEW USER", meta=meta)

        # CREATE TOKEN
        token = base64.urlsafe_b64encode(os.urandom(500))[5:260]
        expire = time.time() + int(config["AUTH"]["TOKEN_EXPIRE"])
        sql = "INSERT INTO AUTH_TOKEN (AUTH_TOKEN_TOKEN, AUTH_TOKEN_PEOPLE_ID, AUTH_TOKEN_EXPIRE) VALUES (?,?,?)"
        db.query(sql, (token,people["PEOPLE_ID"],expire))
        if db.error: return haxdb.data.output(success=0, message=db.error, meta=meta)
        db.commit()
        
        to = "%s %s <%s>" % (people["PEOPLE_NAME_FIRST"], people["PEOPLE_NAME_LAST"], people["PEOPLE_EMAIL"])
        message = message.replace("[token]",token)
        result = tools.send_email(to, subject, message)
        if not result:
            return haxdb.data.output(success=0, message=result, meta=meta)
        return haxdb.data.output(success=1, message="EMAIL SENT", meta=meta)
        
    
    @haxdb.app.route("/AUTH/email/register", methods=["GET","POST"])
    @haxdb.app.route("/AUTH/email/register/<email>", methods=["GET","POST"])
    def mod_auth_register(email=None):
        email = email or haxdb.data.var.get("email")
        subject = haxdb.data.var.get("subject")
        message = haxdb.data.var.get("message")
        
        meta = {}
        meta["api"] = "AUTH/email"
        meta["action"] = "register"
        meta["email"] = email
        meta["subject"] = subject
        meta["message"] = message
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return haxdb.data.output(success=0, message="INVALID VALUE: email", meta=meta)

        email = email.upper()
        sql = "SELECT * FROM PEOPLE WHERE PEOPLE_EMAIL = ?"
        people = db.qaf(sql, (email,))
        if people:
            return haxdb.data.output(success=0, message="USER ALREADY EXISTS", meta=meta)
        
        token = base64.urlsafe_b64encode(os.urandom(500))[5:260]
        expire = int(time.time()) + int(config["AUTH"]["TOKEN_EXPIRE"])
        sql = "INSERT INTO AUTH_TOKEN (AUTH_TOKEN_TOKEN, AUTH_TOKEN_PEOPLE_ID, AUTH_TOKEN_EXPIRE) VALUES (?,?,?)"
        db.query(sql, (token,people["PEOPLE_ID"],expire))
        if db.error: return haxdb.data.output(success=0, message=db.error, meta=meta)
        db.commit()
        
        to = "%s %s <%s>" % (people["PEOPLE_NAME_FIRST"], people["PEOPLE_NAME_LAST"], people["PEOPLE_EMAIL"])
        message = message.replace("[token]",token)
        result = tools.send_email(email, subject, message)

        if not result:
            return haxdb.data.output(success=0, message=result, meta=meta)
        return haxdb.data.output(success=1, message="EMAIL SENT", meta=meta)
        
    
    @haxdb.app.route("/AUTH/token", methods=["GET","POST"])
    @haxdb.app.route("/AUTH/token/<token>", methods=["GET","POST"])
    def mod_auth_token(token=None):
        token = token or haxdb.data.var.get("token")
        config_dbas = [x.strip().upper() for x in config["AUTH"]["DBA"].split(',')]
        now = int(time.time())
        
        meta = {}
        meta["api"] = "AUTH/email"
        meta["action"] = "token"
        meta["token"] = token

        # DELETE OLD TOKEN
        db.query("DELETE FROM AUTH_TOKEN WHERE AUTH_TOKEN_EXPIRE<?", (now,))
        if db.error: return haxdb.data.output(success=0, message=db.error, meta=meta)
        db.commit()
        
        # VALIDATE TOKEN
        sql = """
        SELECT * 
        FROM AUTH_TOKEN
        JOIN PEOPLE ON AUTH_TOKEN_PEOPLE_ID = PEOPLE_ID
        WHERE
        AUTH_TOKEN_TOKEN = ?
        AND AUTH_TOKEN_EXPIRE > ?
        """
        db.query(sql, (token, now,))
        row = db.next()
        if not row:
            return haxdb.data.output(success=0, message="TOKEN IS INVALID OR EXPIRED.\nLOG IN AGAIN.", meta=meta)
        
        # CREATE SESSION NODE
        api_key = base64.urlsafe_b64encode(os.urandom(500))[5:260]
        expire = int(time.time() + 1800) # 30 minutes
        node_name = "%s %s TOKEN AUTH" % (row["PEOPLE_NAME_FIRST"],row["PEOPLE_NAME_LAST"],)
        dba = row["PEOPLE_DBA"]
        if row["PEOPLE_EMAIL"].upper() in config_dbas: dba = 1
        ip = str(request.environ['REMOTE_ADDR'])
        sql = """
        INSERT INTO NODES (NODES_API_KEY,NODES_PEOPLE_ID,NODES_NAME,NODES_READONLY,NODES_DBA,NODES_IP,NODES_EXPIRE,NODES_ENABLED,NODES_QUEUED)
        VALUES (?,?,?,0,?,?,?,1,0)
        """
        db.query(sql,(api_key,row["PEOPLE_ID"],node_name,dba,ip,expire,))
        if db.error: return haxdb.data.output(success=0, message=db.error, meta=meta)
        
        # REMOVE TOKEN
        sql = "DELETE FROM AUTH_TOKEN WHERE AUTH_TOKEN_TOKEN=?"
        db.query(sql, (token,))
        if db.error: return haxdb.data.output(success=0, message=db.error, meta=meta)
        db.commit()
            
        meta["people_name"] = "%s %s" % (row["PEOPLE_NAME_FIRST"], row["PEOPLE_NAME_LAST"])
        return haxdb.data.output(success=1, message="AUTHENTICATED", meta=meta, value=api_key)

