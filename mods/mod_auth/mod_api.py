import os, base64, json, time

api = None
db = None
config = None
tools = None

def init(app_api, app_db, app_config, mod_tools):
    global api, db, config, tools
    api = app_api
    db = app_db
    config = app_config
    tools = mod_tools


def run():
    global api, config, db, tools

    @api.app.before_request
    def mod_api_keys_before_request():
        api.sess.permanent = True
        key = api.data.get("api_key", use_session=True)
        
        if key:
            sql = "select * from API_KEYS where API_KEYS_KEY=?"
            db.query(sql,[key,])
            row = db.next()
            if row and row["API_KEYS_KEY"] == key:
                api.session.set("api_authenticated", 1)
                api.session.set("api_people_id",row["API_KEYS_PEOPLE_ID"])
                api.session.set("api_key_id",row["API_KEYS_ID"])
                api.session.set("api_key",row["API_KEYS_KEY"])
                api.session.set("api_readonly",row["API_KEYS_READONLY"])
                api.session.set("api_dba",row["API_KEYS_DBA"])
        
  
    @api.app.route("/API_KEYS/list", methods=["POST","GET"])
    @api.require_auth
    def mod_api_keys_list():
        people_id = None
        query = api.data.get("query")
        dba = (api.session.get("api_dba") == 1)

        data = {}
        data["input"] = {}
        data["input"]["api"] = "API_KEYS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        data["input"]["dba"] = dba
        
        if query: 
            query = "%" + query + "%"
        else: 
            query = "%"
            
        if dba:
            people_id = api.data.get("people_id")
        else:
            people_id = api.session.get("api_people_id")

        if not people_id and dba:
            sql = "SELECT * FROM API_KEYS JOIN PEOPLE ON API_KEYS_PEOPLE_ID=PEOPLE_ID"
            sql += " WHERE API_KEYS_DESCRIPTION LIKE ? OR API_KEYS_KEY LIKE ?"
            sql += " ORDER BY PEOPLE_EMAIL"
            db.query(sql, (query, query,))
        elif people_id:
            sql = "SELECT * FROM API_KEYS JOIN PEOPLE ON API_KEYS_PEOPLE_ID=PEOPLE_ID"
            sql += " WHERE API_KEYS_PEOPLE_ID = ? and (API_KEYS_DESCRIPTION LIKE ? OR API_KEYS_KEY LIKE ?)"
            db.query(sql,(people_id, query, query,))
        else:
            return api.output(success=0, info="MISSING VALUE: people_id", data=data)

        rows = []
        row = db.next()
        while row:
            rows.append(dict(row))
            row = db.next()

        return api.output(success=1, rows=rows, data=data)

    @api.app.route("/API_KEYS/new", methods=["POST", "GET"])
    @api.require_auth
    @api.no_readonly
    def mod_api_keys_create():
        dba = (api.session.get("api_dba") == 1)

        data = {}
        data["input"] = {}
        data["input"]["api"] = "API_KEYS"
        data["input"]["action"] = "new"
        data["input"]["people_id"] = api.data.get("people_id") or api.session.get("api_people_id")
        data["input"]["dba"] = api.data.get("dba") or 0
        data["input"]["readonly"] = api.data.get("readonly") or 0

        if not dba:
            data["input"]["people_id"] = api.session.get("api_people_id")
            data["input"]["dba"] = 0

        key = tools.create_api_key(data["input"]["dba"], data["input"]["readonly"], data["input"]["people_id"])
                
        if key:
            row = dict(key).copy()
            people = tools.get_people(people_id=data["input"]["people_id"])
            row.update(dict(people))
            rows = {}
            rows[row["API_KEYS_ID"]] = row
            return api.output(success=1, rows=rows, data=data)
        else:
            return api.output(success=0, info=key, data=data)
        
  
        
    
    @api.app.route("/API_KEYS/save", methods=["GET","POST"])
    @api.app.route("/API_KEYS/save/<int:rowid>", methods=["GET","POST"])
    @api.app.route("/API_KEYS/save/<int:rowid>/<col>", methods=["GET","POST"])
    @api.app.route("/API_KEYS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.no_readonly
    def mod_auth_save_api_keys (rowid=None, col=None, val=None):
        valid_cols = ["API_KEYS_DBA","API_KEYS_READONLY","API_KEYS_DESCRIPTION","API_KEYS_IP"]
        limited_cols = ["API_KEYS_DBA","API_KEYS_READONLY","API_KEYS_IP"]
        
        rowid = rowid or api.data.get("rowid")
        col = col or api.data.get("col")
        val = val or api.data.get("val")
        
        dba = (api.session.get("api_dba") == 1)
        people_id = api.session.get("api_people_id")
        key_id = api.session.get("api_key_id")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "API_KEYS"
        data["input"]["action"] = "save"
        data["input"]["col"] = col
        data["input"]["rowid"] = rowid
        data["input"]["val"] = val
        data["oid"] = "API_KEYS-%s-%s" % (rowid,col,)
        
        if col not in valid_cols:
            return api.output(success=0, info="INVALID VALUE: col", data=data)

        if col in limited_cols and int(key_id) == int(rowid):
            return api.output(success=0, info="CANNOT UPDATE KEY YOU ARE CURRENTLY USING", data=data)
        
        if col in ("API_KEYS_DBA","API_KEYS_READONLY") and val not in ("0","1"):
            return api.output(success=0, info="INVALID VALUE: val", data=data)

        if col == "API_KEYS_DBA" and not dba:
            return api.output(success=0, info="INVALID PERMISSION", data=data)
        
        if dba:
            sql = "UPDATE API_KEYS SET %s=? WHERE API_KEYS_ID=?" % (col,)
            db.query(sql,(val, rowid))
        else:
            sql = "UPDATE API_KEYS SET %s=? WHERE API_KEYS_ID=? and API_KEYS_PEOPLE_ID=?" % (col,)
            db.query(sql,(val, rowid, people_id,))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, info="SAVED", data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="INVALID PERMISSION", data=data)
        
    
    @api.app.route("/API_KEYS/delete", methods=["GET","POST"])
    @api.app.route("/API_KEYS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.no_readonly
    def mod_auth_delete_api_keys(rowid=None):
        rowid = rowid or api.data.get("rowid")
        
        dba = (api.session.get("api_dba") == 1)
        people_id = api.session.get("api_people_id")
        key_id = api.session.get("api_key_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "API_KEYS"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        
        if key_id == rowid:
            return api.output(success=0, info="CANNOT DELETE KEY YOU ARE CURRENTLY USING", data=data)
        
        if dba:
            sql = "DELETE FROM API_KEYS WHERE API_KEYS_ID=?"
            db.query(sql,(rowid,))
        else:
            sql = "DELETE FROM API_KEYS WHERE API_KEYS_ID=? AND API_KEYS_PEOPLE_ID=?"
            db.query(sql,(rowid, people_id))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, info="DELETED", data=data)
        
        if db.error:
            return api.output(success=0, info=db.error, data=data)
        
        return api.output(success=0, info="INVALID PERMISSION", data=data)         
    
    
    @api.app.route("/AUTH/email/login", methods=["GET","POST"])
    @api.app.route("/AUTH/email/login/<email>", methods=["GET","POST"])
    def mod_auth_email(email=None):
        email = email or api.data.get("email")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "login"
        data["input"]["email"] = email
        
        if not tools.valid_email(email):
            return api.output(success=0, info="INVALID VALUE: email", data=data)
        
        people = tools.get_people(email)
        if not people:
            return api.output(success=0, info="NEW USER", data=data)
            
        token = tools.create_token(email)
        url = "%sauth/token/%s" % (config["GUI"]["URL"], token)
        subject = "%s AUTHENTICATION" % config["GENERAL"]["ORG"]
        msg = "To authenticate please follow this long and ugly link:\n\n%s" % url
        
        result = tools.send_email(email, subject, msg)
        if not result:
            return api.output(success=0, info=result, data=data)
        return api.output(success=1, info="EMAIL SENT", data=data)
        
    
    @api.app.route("/AUTH/email/register", methods=["GET","POST"])
    @api.app.route("/AUTH/email/register/<email>", methods=["GET","POST"])
    def mod_auth_register(email=None):
        email = email or api.data.get("email")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "register"
        data["input"]["email"] = email

        if not tools.valid_email(email):
            return api.output(success=0, info="INVALID VALUE: email", data=data)

        email = email.upper()
        people = tools.get_people(email)
        if people:
            return api.output(success=0, info="USER ALREADY EXISTS", data=data)
        
        token = tools.create_token(email)
        url = "%sauth/token/%s" % (config["GUI"]["URL"], token)
        subject = "%s REGISTRATION" % config["GENERAL"]["ORG"]
        msg = "To authenticate please follow this long and ugly link:\n\n%s" % url
        
        result = tools.send_email(email, subject, msg)
        if not result:
            return api.output(success=0, info=result, data=data)
        return api.output(success=1, info="EMAIL SENT", data=data)
        
    
    @api.app.route("/AUTH/email/token", methods=["GET","POST"])
    @api.app.route("/AUTH/email/token/<token>", methods=["GET","POST"])
    def mod_auth_token(token=None):
        token = token or api.data.get("token")
        email = tools.verify_token(token)
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "token"
        data["input"]["token"] = token
        
        if not email:
            return api.output(success=0, info="TOKEN IS INVALID OR EXPIRED.\nLOG IN AGAIN.", data=data)
            
        people = tools.get_people(email=email)
        
        if not people:
            people = tools.create_people(email)
            if not people:
                return api.output(success=0, info=people, data=data)

        api_key = tools.get_people_api_key(people["PEOPLE_ID"])
        
        if not api_key:
            return api.output(success=0, info=api_key, data=data)
            
        tools.delete_token(token)

        data["api_key"] = api_key
        data["email"] = people["PEOPLE_EMAIL"]
        
        return api.output(success=1, info="AUTHENTICATED", data=data)

    @api.app.route("/AUTH/email/session", methods=["POST","GET"])
    @api.require_auth
    def mod_api_keys_session():
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "session"

        data["readonly"] = api.session.get("api_readonly")
        data["dba"] = api.session.get("api_dba")
        data["member_id"] = api.session.get("member_id")
        return api.output(success=1, info="SESSION VALID", data=data)    