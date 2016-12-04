import tables
       
class db:
    db = None
    tables = tables
    config = None
    
    def __init__(self, config):
        self.config = config
        
    def open(self):
        if self.config["TYPE"] == "SQLITE":
            import driver_sqlite
            self.db = driver_sqlite.db(self.config)
        elif self.config["TYPE"] == "MARIADB":
            import driver_mariadb
            self.db = driver_mariadb.db(self.config)
        
    def close(self):
        self.db.close()
        
    def create(self, tables, indexes):
        return self.db.create(tables, indexes)
        
    def query(self, sql, data=None, squelch=False):
        self.rowcount = None
        self.lastrowid = None
        self.error = None
        result = self.db.query(sql, data, squelch)
        self.rowcount = self.db.rowcount
        self.lastrowid = self.db.lastrowid
        self.error = self.db.error
        return result
    
    def qaf (self, sql, data=None):
        self.query(sql, data)
        if self.error:
            return False
        return self.next()
    
    def next(self):
        return self.db.next()
    
    def commit(self):
        return self.db.commit()
    
    def rollback(self):
        return self.db.rollback()
    
        