import mysql.connector as mariadb

class db:

    def __init__( self, config ):
        self.conn = mariadb.connect(host=config["HOST"], port=config["PORT"], user=config["USER"], password=config["PASS"], database=config["DB"])
        self.cur = self.conn.cursor(dictionary=True)
    
    def get_datatype(self, datatype, datasize):
        if datatype == "INT":
            return "INT" if not datasize else "INT(%s)" % str(datasize)
        
        if datatype == "VARCHAR" or datatype == "CHAR":
            return "VARCHAR(50)" if not datasize else "VARCHAR(%s)" % str(datasize)

        if datatype == "ASCII":
            return "VARCHAR(50) CHARSET ASCII" if not datasize else "VARCHAR(%s) CHARSET ASCII" % str(datasize)
        
        if datatype == "BOOL":
            return "INT(1)"
        
        if datatype == "FLOAT":
            return "FLOAT(5,2)" if not datasize else "FLOAT(%s,4)" % str(datasize)

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
                create_table_sql += "%s_ID INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT" % table.name
                create_table_sql += ", %s_INSERTED TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00'" % table.name
                create_table_sql += ", %s_UPDATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP" % table.name
                create_table_sql += ")"
                self.query(create_table_sql, squelch=True)
                self.commit()
                
                trigger_sql = """
                CREATE TRIGGER trigger_%s_INSERT_timestamp BEFORE INSERT ON %s
                FOR EACH ROW SET NEW.%s_UPDATED = NULL, NEW.%s_INSERTED = NULL;
                """ % (table.name, table.name, table.name, table.name)
                self.query(trigger_sql, squelch=True)
                self.commit()

                self.query("SET FOREIGN_KEY_CHECKS=0")
                for col in table:
                    params = ()
                    sql = "ALTER TABLE %s ADD COLUMN %s %s" % (table.name, col.name, self.get_datatype(col.datatype, col.size))
                    if col.required:
                        sql += " NOT NULL"
                    self.query(sql, squelch=True)

                    if col.fk_table and col.fk_col:
                        sql = "ALTER TABLE %s ADD CONSTRAINT fk_%s_%s FOREIGN KEY (%s) REFERENCES %s(%s) ON DELETE CASCADE" % (table.name, table.name, col.name, col.name, col.fk_table, col.fk_col)
                        self.query(sql, squelch=True)
                        
                    self.commit()
                self.query("SET FOREIGN_KEY_CHECKS=1")
                    
                
    def create_indexes(self, indexes):
        if indexes:
            for idx in indexes:
                idx_name = "IDX_" + "_".join(idx.cols)
                idx_sql = "CREATE"
                if idx.unique: idx_sql += " UNIQUE"
                idx_sql += " INDEX %s ON %s (%s)" % (idx_name, idx.table, ",".join(idx.cols))
                self.query(idx_sql, squelch=True)
                
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
        except mariadb.Error as error:
            self.error = str(error)
            if not squelch:  
                print "\n########################################\n"
                print "SQL ERROR: %s" % self.error
                print data
                print "-----------------------------------"
                print sql
                print "\n########################################\n"
            
    
    def next ( self ):
        return self.cur.fetchone()

    def commit(self):
        return self.conn.commit()
        
    def rollback(self):
        return self.conn.rollback()
    
    def close(self):
        self.conn.close()