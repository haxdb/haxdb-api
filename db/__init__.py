import tables
        
class db:
    db = None
    tables = tables
    
    def __init__(self, config):
        if config["TYPE"] == "SQLITE":
            import sqlite
            self.db = sqlite.db(config)
        
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
    
    def table_exists(self, table):
        return self.db.table_exists(table)
    
    def commit(self):
        return self.db.commit()
    
    def rollback(self):
        return self.db.rollback()
    
        