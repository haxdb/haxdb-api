import mod_data
from flask import request
import time

haxdb = None
db = None
config = None
tools = None
apis = {}

def init(app_haxdb, app_db, app_config, mod_tools):
    global haxdb, db, config, tools, apis
    haxdb = app_haxdb
    db = app_db
    config = app_config
    tools = mod_tools

    for api_name in mod_data.apis:
        apis[api_name] = haxdb.api.api_call()
        apis[api_name].lists = mod_data.apis[api_name]["lists"]
        apis[api_name].cols = mod_data.apis[api_name]["cols"]
        apis[api_name].query_cols = mod_data.apis[api_name]["query_cols"]
        apis[api_name].search_cols = mod_data.apis[api_name]["search_cols"]
        apis[api_name].order_cols = mod_data.apis[api_name]["order_cols"]


def run():
    @haxdb.app.route("/RFID/asset/auth", methods=["POST", "GET"])
    @haxdb.app.route("/RFID/asset/auth/<rfid>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/auth", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/auth/<rfid>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_rfid_asset_auth(rfid=None):
        api_key = haxdb.session.get("api_key")
        rfid = rfid or haxdb.data.var.get("rfid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS_RFID"
        data["input"]["action"] = "auth"
        data["input"]["rfid"] = rfid

        sql = """
        SELECT * FROM NODES 
        JOIN ASSETS ON ASSETS_ID=NODES_ASSETS_ID
        LEFT OUTER JOIN ASSETS_RFID ON ASSETS_RFID_ASSETS_ID = ASSETS_ID
        WHERE
        NODES_API_KEY = ?
        """
        db.query(sql,(api_key,))
        if db.error:
            return haxdb.data.output(success=0, data=data, info=db.error)
      
        row = db.next()
        if not row:
            return haxdb.data.output(success=0, data=data, message="NO NODE/ASSET RELATIONSHIP")

        assets_id = row["ASSETS_ID"]
        assets_name = row["ASSETS_NAME"]
        require_auth = row["ASSETS_RFID_REQUIRE_AUTH"]
        auto_log = row["ASSETS_RFID_AUTO_LOG"]
        data["assets_id"] = assets_id
        auth_people_id = row["ASSETS_RFID_AUTH_PEOPLE_ID"]
        auth_start = row["ASSETS_RFID_AUTH_START"]
        auth_timeout = row["ASSETS_RFID_AUTH_TIMEOUT"]
        auth_last = row["ASSETS_RFID_AUTH_LAST"]
        
        if row["ASSETS_RFID_REQUIRE_AUTH"] == None:
            return haxdb.data.output(success=0, data=data, message="AUTH NOT CONFIGURED FOR ASSET: %s" % (assets_name,))
        
        if int(row["ASSETS_RFID_REQUIRE_AUTH"]) != 1:
            return haxdb.data.output(success=1, data=data, message="NO AUTH REQUIRED FOR ASSET: %s" % (assets_name,))
            
        sql = """
        SELECT
        PEOPLE_ID, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        A.ASSETS_NAME
        
        FROM PEOPLE
        JOIN ASSET_AUTHS AA ON AA.ASSET_AUTHS_PEOPLE_ID = P.PEOPLE_ID
        JOIN ASSETS A ON A.ASSETS_ID = AA.ASSET_AUTHS_ASSETS_ID
        JOIN PEOPLE_RFID ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_RFID_RFID != '' and PEOPLE_RFID_RFID IS NOT NULL
        
        WHERE
        PEOPLE_RFID_RFID = ?
        AND AA.ASSET_AUTHS_ASSETS_ID = ?
        """
        db.query(sql, (rfid,assets_id,))
        
        if db.error:
            return haxdb.data.output(success=0, data=data, message=db.error)

        row = db.next()
        if row:
            data["row"] = dict(row)
            
            auth_now = time.time()
            if row["PEOPLE_ID"] == auth_people_id and (auth_now-auth_last) < auth_timeout:
                sql = "UPDATE ASSETS_RFID SET ASSETS_RFID_AUTH_LAST=? WHERE ASSETS_RFID_ASSETS_ID=?"
                db.query(sql,(auth_now,assets_id))
            else:
                sql = "UPDATE ASSETS_RFID SET ASSETS_RFID_AUTH_PEOPLE_ID=?, ASSETS_RFID_AUTH_START=?, ASSETS_RFID_AUTH_LAST=?  WHERE ASSETS_RFID_ASSETS_ID=?"
                db.query(sql,(row["PEOPLE_ID"],auth_now,auth_now,assets_id))
                if auto_log and int(auto_log) == 1:
                    description = "%s %s %s on %s" % (row["PEOPLE_NAME_FIRST"], row["PEOPLE_NAME_LAST"], "RFID AUTH", row["ASSETS_NAME"])
                    tools.log(row["PEOPLE_ID"], "RFID AUTH", assets_id, description)

            return haxdb.data.output(success=1, data=data, message="SUCCESS")
        
        if auto_log and int(auto_log) == 1:
            sql = """
                SELECT
                P.PEOPLE_ID, PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST, A.ASSETS_NAME
                FROM PEOPLE P
                JOIN ASSETS A 
                JOIN PEOPLE_RFID ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_RFID_RFID != '' and PEOPLE_RFID_RFID IS NOT NULL
                WHERE
                AND PEOPLE_RFID_RFID = ?
                AND A.ASSETS_ID = ?
                """
            db.query(sql, (rfid, assets_id))
            row = db.next()
            if row:
                description = "%s %s DENY ON %s" % (row["PEOPLE_NAME_FIRST"], row["PEOPLE_NAME_LAST"], row["ASSETS_NAME"])
                tools.log(row["PEOPLE_ID"], "RFID DENY", assets_id, description)
            else:
                description = "UNKNOWN USER ATTEMPT ON %s" % (assets_name,)
                tools.log(None, "RFID DENY", assets_id, description)

        return haxdb.data.output(success=0, message="ASSET: %s\nPERMISSION DENIED" % (assets_name,), data=data)


    @haxdb.app.route("/ASSETS_RFID/deauth", methods=["POST", "GET"])
    def mod_rfid_asset_deauth():
        api_key = haxdb.session.get("api_key")
        
    @haxdb.app.route("/RFID/asset/register", methods=["POST", "GET"])
    @haxdb.app.route("/RFID/asset/register/<rfid>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/register", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/register/<rfid>", methods=["POST", "GET"])
    def mod_rfid_asset_register(rfid=None):
        rfid = rfid or haxdb.data.var.get("rfid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS_RFID"
        data["input"]["action"] = "register"
        data["input"]["rfid"] = rfid
        
        sql = """
        SELECT 
        PEOPLE_ID, 
        PFN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_FIRST_NAME,
        PLN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_LAST_NAME
        FROM PEOPLE
        JOIN PEOPLE_COLUMNS PC ON PC.PEOPLE_COLUMNS_NAME='RFID'
        JOIN PEOPLE_COLUMN_VALUES PCV ON PCV.PEOPLE_COLUMN_VALUES_PEOPLE_ID=PEOPLE_ID AND PCV.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PC.PEOPLE_COLUMNS_ID
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PFN ON PFN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PFN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PLN ON PLN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PLN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')
        WHERE
        PCV.PEOPLE_COLUMN_VALUES_VALUE=? 
        AND PEOPLE_DBA='1'
        """
        db.query(sql, (rfid,))
        if db.error:
            return haxdb.data.output(success=0, data=data, message=db.error)
        
        people = db.next()
        if not people:
            return haxdb.data.output(success=0, data=data, message="INVALID RFID")
        
        sql = """
        INSERT INTO NODES (NODES_API_KEY, NODES_PEOPLE_ID, NODES_NAME, NODES_READONLY, NODES_DBA, NODES_IP, NODES_ENABLED, NODES_STATUS)
        VALUES (?,?,?,'1','0',?,'0','0')
        """
        api_key = tools.create_api_key()
        node_name = "%s %s REGISTERED (RFID)" % (people["PEOPLE_FIRST_NAME"],people["PEOPLE_LAST_NAME"])
        ip = str(request.environ['REMOTE_ADDR'])
        db.query(sql, (api_key,people["PEOPLE_ID"],node_name,ip,))
        
        if db.rowcount > 0:
            db.commit()
            data["api_key"] = api_key
            description = "%s %s REGISTERED A NODE WITH RFID" % (people["PEOPLE_FIRST_NAME"],people["PEOPLE_LAST_NAME"])
            tools.log(people["PEOPLE_ID"], "REGISTER", None, description,db.lastrowid)
            return haxdb.data.output(success=1, data=data, message="NODE REGISTERED")
        
        return haxdb.data.output(success=0, data=data, message="UNKNOWN ERROR")
    

    @haxdb.app.route("/RFID/asset/list", methods=["POST", "GET"])
    @haxdb.app.route("/RFID/asset/list/<path:query>", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/list", methods=["POST", "GET"])
    @haxdb.app.route("/ASSETS_RFID/list/<path:query>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_rfid_asset_list(query=None):
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS_RFID"
        data["input"]["action"] = "list"

        sql = """
        SELECT *, 
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM ASSETS_RFID
        JOIN ASSETS ON ASSETS_ID = ASSETS_RFID_ASSETS_ID
        LEFT OUTER JOIN PEOPLE ON ASSETS_RFID_AUTH_PEOPLE_ID=PEOPLE_ID
        """
        return apis["ASSETS_RFID"].list_call(sql, (), data)
    
    @haxdb.app.route("/ASSETS_RFID/view", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS_RFID/view/<int:rowid>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_ASSETS_RFID_view(rowid=None):
        def calc_row(row):
            row["ASSETS_RFID_IN_USE"] = 0
            if row["ASSETS_RFID_AUTH_LAST"] and row["ASSETS_RFID_AUTH_TIMEOUT"]  and (time.time() - int(row["ASSETS_RFID_AUTH_LAST"])) < row["ASSETS_RFID_AUTH_TIMEOUT"]:
                row["ASSETS_RFID_IN_USE"] = 1
            return row
        
        rowid = rowid or haxdb.data.var.get("rowid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS_RFID"
        data["input"]["action"] = "view"
        data["input"]["rowid"] = rowid

        sql = """SELECT ASSETS.*, ASSETS_RFID.*, 
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM ASSETS        
        LEFT OUTER JOIN ASSETS_RFID ON ASSETS_ID = ASSETS_RFID_ASSETS_ID
        LEFT OUTER JOIN PEOPLE ON ASSETS_RFID_AUTH_PEOPLE_ID=PEOPLE_ID
        WHERE
        ASSETS_ID=?
        """
        params = (rowid,)
        return apis["ASSETS_RFID"].view_call(sql, params, data, calc_row)
        
    
    @haxdb.app.route("/ASSETS_RFID/save", methods=["POST","GET"])
    @haxdb.app.route("/ASSETS_RFID/save/<int:rowid>/<col>/<path:val>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_ASSETS_RFID_save(rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "ASSETS_RFID"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        
        sql = "INSERT INTO ASSETS_RFID(ASSETS_RFID_ASSETS_ID) VALUES (?)"
        db.query(sql,(rowid,), squelch=True)
        db.commit()

        sql = """
        UPDATE ASSETS_RFID SET %s = ? WHERE ASSETS_RFID_ASSETS_ID = ?
        """
        params = (val, rowid,)
        
        return apis["ASSETS_RFID"].save_call(sql,params,data,col,val)
    
    @haxdb.app.route("/PEOPLE_RFID/list", methods=["POST","GET"])
    @haxdb.app.route("/PEOPLE_RFID/list/<int:people_id>", methods=["POST","GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    def mod_PEOPLE_RFID_list (people_id=None):
        people_id = people_id or haxdb.data.var.get("people_id")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_RFID"
        data["input"]["action"] = "list"
        data["input"]["people_id"] = people_id

        sql = "SELECT * FROM PEOPLE WHERE PEOPLE_ID=?"
        row = db.qaf(sql,(people_id,))
        data["verbose"] = dict(row)
        
        sql = """
        SELECT *,
        PEOPLE_NAME_FIRST, PEOPLE_NAME_LAST
        FROM PEOPLE_RFID
        JOIN PEOPLE ON PEOPLE_RFID_PEOPLE_ID=PEOPLE_ID AND PEOPLE_ID=?
        """
        params = (people_id,)
        return apis["PEOPLE_RFID"].list_call(sql, params, data)
    
    @haxdb.app.route("/PEOPLE_RFID/new", methods=["POST", "GET"])
    @haxdb.app.route("/PEOPLE_RFID/new/<int:people_id>/<name>", methods=["POST", "GET"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_new(people_id=None, name=None):
        people_id = people_id or haxdb.data.var.get("people_id")
        name = name or haxdb.data.var.get("name")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_RFID"
        data["input"]["action"] = "new"
        data["input"]["people_id"] = people_id
        data["input"]["name"] = name
        
        sql = "INSERT INTO PEOPLE_RFID (PEOPLE_RFID_PEOPLE_ID, PEOPLE_RFID_NAME, PEOPLE_RFID_ENABLED) "
        sql += "VALUES (?, ?, 0)"
        params = (people_id, name,)
        return apis["PEOPLE_RFID"].new_call(sql, params, data)
    
    @haxdb.app.route("/PEOPLE_RFID/save", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE_RFID/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_save (rowid=None, col=None, val=None):
        rowid = rowid or haxdb.data.var.get("rowid")
        col = col or haxdb.data.var.get("col")
        val = val or haxdb.data.var.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_RFID"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = col
        data["input"]["val"] = val
        data["oid"] = "PEOPLE_RFID-%s-%s" % (rowid, col,)
        
        sql = "UPDATE PEOPLE_RFID SET %s=? WHERE PEOPLE_RFID_ID=?" 
        params = (val,rowid,)
        return apis["PEOPLE_RFID"].save_call(sql, params, data, col, val, rowid)
    
    @haxdb.app.route("/PEOPLE_RFID/delete", methods=["GET","POST"])
    @haxdb.app.route("/PEOPLE_RFID/delete/<int:rowid>", methods=["GET","POST"])
    @haxdb.require_auth
    @haxdb.require_dba
    @haxdb.no_readonly
    def mod_PEOPLE_RFID_delete(rowid=None):
        rowid = rowid or haxdb.data.var.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_RFID"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        sql = "DELETE FROM PEOPLE_RFID WHERE PEOPLE_RFID_ID=?"
        params = (rowid,)
        return apis["PEOPLE_RFID"].delete_call(sql, params, data)    