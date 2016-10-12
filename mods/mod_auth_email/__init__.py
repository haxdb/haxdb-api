import mod_db, mod_api
import mod_tools

db = None
config = None
api = None

def init(app_config, app_db, app_api):
    global config, db, api
    config = app_config
    db = app_db
    api = app_api
    
    mod_tools.init(config, db, api)
    mod_db.init(db,config)
    mod_api.init(api,db,config,mod_tools)
    
    
def run ():
    mod_db.run()
    mod_api.run()
    
