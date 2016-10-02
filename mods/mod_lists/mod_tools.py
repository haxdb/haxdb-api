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
    

api = None
db = None
config = None

def init(app_config, app_db, app_api):
    global api, db, config
    api = app_api
    db = app_db
    config = app_config
    
def is_float(val):
    try:
        float(val)
        return True
    except:
        return False
    