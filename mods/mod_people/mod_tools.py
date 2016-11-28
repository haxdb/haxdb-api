import time, base64, re, os

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

def get_col_options(col_name):
    col = get_col_definition(col_name)
    sql = """
    SELECT * FROM LISTS
    JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID = LISTS_ID
    WHERE
    LISTS_ID = ?
    """
    db.query(sql,(col['PEOPLE_COLUMNS_LISTS_ID'],))
    options = []
    row = db.next()
    while row:
        options.append(row["LIST_ITEMS_VALUE"])
        row = db.next()
    return options

def get_col_definition(col_name):
    sql = "SELECT * FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_NAME=?"
    db.query(sql, (col_name,))
    return db.next()

def valid_col_value(col_name, col_type, col_value):

    if col_type in ["TEXT","TEXTAREA","STATIC","HIDDEN","DATE"]:
        return True
    
    if col_type in ("INTEGER","INT"):
        try:
            int(col_value)
            return True
        except ValueError:
            return False
        
    if col_type in ("FLOAT","NUMERIC"):
        try:
            float(col_value)
            return True
        except ValueError:
            return False
        
    if col_type == "CHECKBOX":
        try:
            if int(col_value) in (0,1):
                return True
        except:
            return False
        
    if col_type == "LIST":
        options = get_col_options(col_name)
        if col_value in options:
            return True
        
    return False

def get_keycols(rowid,withnone=False):
    sql = """
    SELECT * FROM PEOPLE
    JOIN PEOPLE_COLUMNS ON PEOPLE_COLUMNS_KEY=1
    LEFT OUTER JOIN PEOPLE_COLUMN_VALUES ON PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PEOPLE_COLUMNS_ID AND PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID
    WHERE PEOPLE_ID=?
    ORDER BY PEOPLE_COLUMNS_ORDER
    """
    db.query(sql, (rowid,))
    key_cols = []
    row = db.next()
    while row:
        if row["PEOPLE_COLUMN_VALUES_VALUE"]:
            key_cols.append(row["PEOPLE_COLUMN_VALUES_VALUE"])
        row = db.next()
    
    return key_cols
    