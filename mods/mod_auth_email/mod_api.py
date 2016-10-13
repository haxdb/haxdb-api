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

    @api.app.route("/AUTH/email/login", methods=["GET","POST"])
    @api.app.route("/AUTH/email/login/<email>", methods=["GET","POST"])
    def mod_auth_email(email=None):
        email = email or api.data.get("email")
        subject = api.data.get("subject")
        message = api.data.get("message")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "login"
        data["input"]["email"] = email
        data["input"]["subject"] = subject
        data["input"]["message"] = message
        
        if not tools.valid_email(email):
            return api.output(success=0, message="INVALID VALUE: email", data=data)
        
        people = tools.get_people(email)
        if not people:
            return api.output(success=0, message="NEW USER", data=data)
            
        token = tools.create_token(email)
        message = message.replace("[token]",token)
        
        result = tools.send_email(email, subject, message)
        if not result:
            return api.output(success=0, message=result, data=data)
        return api.output(success=1, message="EMAIL SENT", data=data)
        
    
    @api.app.route("/AUTH/email/register", methods=["GET","POST"])
    @api.app.route("/AUTH/email/register/<email>", methods=["GET","POST"])
    def mod_auth_register(email=None):
        email = email or api.data.get("email")
        subject = api.data.get("subject")
        message = api.data.get("message")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "register"
        data["input"]["email"] = email
        data["input"]["subject"] = subject
        data["input"]["message"] = message
        
        if not tools.valid_email(email):
            return api.output(success=0, message="INVALID VALUE: email", data=data)

        email = email.upper()
        people = tools.get_people(email)
        if people:
            return api.output(success=0, message="USER ALREADY EXISTS", data=data)
        
        token = tools.create_token(email)
        message = message.replace("[token]",token)
        
        result = tools.send_email(email, subject, message)
        if not result:
            return api.output(success=0, message=result, data=data)
        return api.output(success=1, message="EMAIL SENT", data=data)
        
    
    @api.app.route("/AUTH/email/token", methods=["GET","POST"])
    @api.app.route("/AUTH/email/token/<token>", methods=["GET","POST"])
    def mod_auth_token(token=None):
        token = token or api.data.get("token")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "AUTH/email"
        data["input"]["action"] = "token"
        data["input"]["token"] = token

        # VALIDATE TOKEN
        db.query("SELECT * FROM AUTH_TOKEN WHERE AUTH_TOKEN_TOKEN=? AND AUTH_TOKEN_EXPIRE>?", (token,time.time()))
        row = db.next()
        if row and row["AUTH_TOKEN_EMAIL"] and row["AUTH_TOKEN_TOKEN"] == token:
            email = row["AUTH_TOKEN_EMAIL"]
        else:
            return api.output(success=0, message="TOKEN IS INVALID OR EXPIRED.\nLOG IN AGAIN.", data=data)
        
        # GET MATCHING PEOPLE
        people = tools.get_people(email=email)
        if not people:
            people = tools.create_people(email)
            if not people:
                return api.output(success=0, message=people, data=data)

        # GET API KEY
        api_key = tools.get_people_api_key(people["PEOPLE_ID"])
        
        if not api_key:
            return api.output(success=0, message=str(api_key), data=data)
            
        tools.delete_token(token)

        data["api_key"] = api_key
        data["email"] = people["PEOPLE_EMAIL"]
        
        return api.output(success=1, message="AUTHENTICATED", data=data)

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
        return api.output(success=1, message="SESSION VALID", data=data)    