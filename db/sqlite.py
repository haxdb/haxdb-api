import sqlite3

class db:

    def __init__( self, config ):
        self.conn = sqlite3.connect(config["HOST"])
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA journal_mode=WAL")
        self.cur.execute("PRAGMA foreign_keys=ON")
    
    def get_datatype(self, datatype):
        if datatype == "INT":
            return "INTEGER"
        if datatype == "VARCHAR" or datatype == "CHAR":
            return "VARCHAR"
        if datatype == "BOOL":
            return "INTEGER(1)"
        if datatype == "FLOAT":
            return "REAL"
        if datatype == "TEXT":
            return "TEXT"
        if datatype == "BLOB":
            return "BLOB"
        if datatype == "DATETIME":
            return "INTEGER"
        
    def create(self, tables=None, indexes=None):
        self.create_tables(tables)
        self.create_indexes(indexes)

    def create_tables(self, tables):
        if tables:
            for table in tables:
                create_table_sql = "CREATE TABLE IF NOT EXISTS %s (" % table.name
                create_table_sql += "%s_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT" % table.name
                create_table_sql += ", %s_INSERTED TIMESTAMP NOT NULL DEFAULT current_timestamp" % table.name
                create_table_sql += ", %s_UPDATED TIMESTAMP NOT NULL DEFAULT current_timestamp" % table.name
                
                create_table_sql += ")"
                self.query(create_table_sql, squelch=True)
                self.commit()
                
                trigger_sql = """
                CREATE TRIGGER trigger_%s_update_timestamp AFTER UPDATE ON %s
                BEGIN
                  update %s SET %s_UPDATED = current_timestamp WHERE %s_ID = NEW.%s_ID;
                END;
                """ % (table.name, table.name, table.name, table.name, table.name, table.name)
                self.query(trigger_sql, squelch=True)
                self.commit()

                self.query("PRAGMA foreign_keys = 0")
                for col in table:
                    params = ()
                    sql = "ALTER TABLE %s ADD COLUMN %s %s" % (table.name, col.name, self.get_datatype(col.datatype))
                    if col.size:
                        sql += "(%s)" % (str(col.size))
                    if col.required:
                        sql += " NOT NULL DEFAULT ''"
                    if col.fk_table and col.fk_col:
                        sql += " REFERENCES %s(%s) ON DELETE CASCADE" % (col.fk_table, col.fk_col)
                    self.query(sql, squelch=True)
                    self.commit()
                self.query("PRAGMA foreign_keys = 1")
                    
                
    def create_tables2(self, tables):
        if tables:
            for table in tables:
                key_sql = ""
                sql = "CREATE TABLE IF NOT EXISTS %s (" % table.name
                sql += "%s_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT," % table.name
                total = 0
                for col in table:
                    if col.fk_table and col.fk_col:
                        if key_sql:  key_sql += ","
                        key_sql += "FOREIGN KEY(%s) REFERENCES %s(%s) ON DELETE CASCADE" % (col.name, col.fk_table, col.fk_col)
                    if total > 0:
                        sql += ","
                    sql += "%s %s" % (col.name, self.get_datatype(col.datatype))
                    if col.size:
                        sql += "(%s)" % (str(col.size))
                    if col.required:
                        sql += " NOT NULL"
                    total += 1
                sql += ", %s_INSERTED TIMESTAMP NOT NULL DEFAULT current_timestamp" % table.name
                sql += ", %s_UPDATED TIMESTAMP NOT NULL DEFAULT current_timestamp" % table.name
                if key_sql: sql += "," + key_sql
                sql += ")"
                self.query(sql)
                if self.error:
                    print self.error
                    print sql
                    
                trigger_sql = """
                CREATE TRIGGER trigger_%s_update_timestamp AFTER UPDATE ON %s
                BEGIN
                  update %s SET %s_UPDATED = current_timestamp WHERE %s_ID = NEW.%s_ID;
                END;
                """ % (table.name, table.name, table.name, table.name, table.name, table.name)
                self.query(trigger_sql)
                self.commit()
            
    def create_indexes(self, indexes):
        if indexes:
            for idx in indexes:
                idx_name = "IDX_" + "_".join(idx.cols)
                idx_sql = "CREATE"
                if idx.unique: idx_sql += " UNIQUE"
                idx_sql += " INDEX IF NOT EXISTS %s ON %s (%s)" % (idx_name, idx.table, ",".join(idx.cols))
                self.query(idx_sql)
                
    def query ( self, sql, data=None, squelch=False):
        self.rowcount = None
        self.lastrowid = None
        self.error = None
        try:
            if data:
                result = self.cur.execute(sql,data)
            else:
                result = self.cur.execute(sql) 
            self.rowcount = self.cur.rowcount
            self.lastrowid = self.cur.lastrowid
            return result
        except sqlite3.Error as er:
            self.error = er.message
            if not squelch:  
                print "\n########################################\n"
                print "SQL ERROR: %s" % self.error
                print data
                print "-----------------------------------"
                print sql
                print "\n########################################\n"
            
    
    def next ( self ):
        return self.cur.fetchone()

    def table_exists (self, table):
        self.query("select * from sqlite_master where type='table' and name=%s", (table,))
        row = self.next()
        return (name in row and row["name"] == table)
    
    def get_cols (self, table):
        rows = []
        self.query("PRAGMA table_info(%s)" % table)
        row = self.next()
        while row:
            print dict(row)
            rows.append(row["name"])
            self.next()
        return rows
    
    def commit(self):
        return self.conn.commit()
        
    def rollback(self):
        return self.conn.rollback()