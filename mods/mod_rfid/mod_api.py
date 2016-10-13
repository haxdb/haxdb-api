from flask import request

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
    @api.app.route("/RFID/asset/auth", methods=["POST", "GET"])
    @api.app.route("/RFID/asset/auth/<rfid>", methods=["POST", "GET"])
    @api.require_auth
    @api.require_dba
    def mod_rfid_asset_auth(rfid=None):
        api_key = api.session.get("api_key")
        rfid = rfid or api.data.get("rfid")
        action = api.data.get("action") or "AUTHENTICATE"
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "RFID/asset"
        data["input"]["action"] = "auth"
        data["input"]["rfid"] = rfid

        sql = "SELECT * FROM NODES WHERE NODES_API_KEY = ?"
        db.query(sql,(api_key,))
        if db.error:
            return api.output(success=0, data=data, info=db.error)
      
        row = db.next()
        if not row:
            return api.output(success=0, data=data, message="NO NODE/ASSET RELATIONSHIP")
        assets_id = row["NODES_ASSETS_ID"]
        data["assets_id"] = assets_id
        
        sql = """
        SELECT
        P.PEOPLE_ID,
        PFN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_FIRST_NAME,
        PLN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_LAST_NAME,
        A.ASSETS_NAME
        
        FROM PEOPLE P
        JOIN PEOPLE_COLUMNS PC 
        JOIN PEOPLE_COLUMN_VALUES PCV ON PCV.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PC.PEOPLE_COLUMNS_ID AND PCV.PEOPLE_COLUMN_VALUES_PEOPLE_ID = P.PEOPLE_ID
        JOIN ASSET_AUTHS AA ON AA.ASSET_AUTHS_PEOPLE_ID = P.PEOPLE_ID
        JOIN ASSETS A ON A.ASSETS_ID = AA.ASSET_AUTHS_ASSETS_ID
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PFN ON PFN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PFN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PLN ON PLN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PLN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')

        WHERE
        PC.PEOPLE_COLUMNS_NAME='RFID'
        AND PCV.PEOPLE_COLUMN_VALUES_VALUE = ?
        AND AA.ASSET_AUTHS_ASSETS_ID = ?
        """
        db.query(sql, (rfid,assets_id,))
        
        if db.error:
            return api.output(success=0, data=data, message=db.error)

        row = db.next()
        
        if row:
            description = "%s %s %s on %s" % (row["PEOPLE_FIRST_NAME"], row["PEOPLE_LAST_NAME"], action, row["ASSETS_NAME"])
            tools.log(row["PEOPLE_ID"], action, assets_id, description)
            data["row"] = dict(row)
            return api.output(success=1, data=data, message="SUCCESS")
        
        sql = """
            SELECT
            P.PEOPLE_ID,
            PFN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_FIRST_NAME,
            PLN.PEOPLE_COLUMN_VALUES_VALUE as PEOPLE_LAST_NAME,
            A.ASSETS_NAME
    
            FROM PEOPLE P
            JOIN PEOPLE_COLUMNS PC 
            JOIN PEOPLE_COLUMN_VALUES PCV ON PCV.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PC.PEOPLE_COLUMNS_ID AND PCV.PEOPLE_COLUMN_VALUES_PEOPLE_ID = P.PEOPLE_ID
            JOIN ASSETS A
            LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PFN ON PFN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PFN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='FIRST_NAME')
            LEFT OUTER JOIN PEOPLE_COLUMN_VALUES PLN ON PLN.PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID AND PLN.PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = (SELECT PEOPLE_COLUMNS_ID FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME='LAST_NAME')
    
            WHERE
            PC.PEOPLE_COLUMNS_NAME='RFID'
            AND PCV.PEOPLE_COLUMN_VALUES_VALUE = ?
            AND A.ASSETS_ID = ?
            """
        db.query(sql, (rfid, assets_id))
        row = db.next()
        if row:
            description = "%s %s DENY on %s" % (row["PEOPLE_FIRST_NAME"], row["PEOPLE_LAST_NAME"], row["ASSETS_NAME"])
            tools.log(row["PEOPLE_ID"], "DENY", assets_id, description)

        return api.output(success=0, message="FAIL", data=data)

    @api.app.route("/RFID/asset/register", methods=["POST", "GET"])
    @api.app.route("/RFID/asset/register/<rfid>", methods=["POST", "GET"])
    def mod_rfid_asset_register(rfid=None):
        rfid = rfid or api.data.get("rfid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "RFID/asset"
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
            return api.output(success=0, data=data, message=db.error)
        
        people = db.next()
        if not people:
            return api.output(success=0, data=data, message="INVALID RFID")
        
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
            return api.output(success=1, data=data, message="NODE REGISTERED")
        
        return api.output(success=0, data=data, message="UNKNOWN ERROR")