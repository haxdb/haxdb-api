import base64,os

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
    
def log(people_id, actions_name, assets_id, description, log_nodes_id=None):
    
    sql = """
    SELECT * FROM LISTS
    JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID = LISTS_ID
    WHERE LISTS_NAME='LOG ACTIONS'
    AND LIST_ITEMS_VALUE = %s
    """
    db.query(sql, (actions_name,))
    row = db.next()
    if not row:
        return False
    
    actions_id = row["LIST_ITEMS_ID"]
    log_nodes_id = log_nodes_id or haxdb.session.get("nodes_id")
    
    sql = """
    INSERT INTO LOGS (LOGS_ASSETS_ID, LOGS_ACTION_ID, LOGS_ACTION_PEOPLE_ID, LOGS_DESCRIPTION, LOGS_NODES_ID)
    VALUEs (%s, %s, %s, %s, %s)
    """
    db.query(sql, (assets_id, actions_id, people_id, description, log_nodes_id,))
    db.commit()
    
    
def create_api_key():
    return base64.urlsafe_b64encode(os.urandom(500))[5:260]
    