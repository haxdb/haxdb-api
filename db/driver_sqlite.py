import sqlite3


class db:

    logger = None

    def __init__(self, config, logger):
        self.logger = logger
        self.conn = sqlite3.connect(config["HOST"])
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA journal_mode=WAL")
        self.cur.execute("PRAGMA foreign_keys=ON")

    def _TOBLOB(self, data):
        return sqlite3.Binary(data)

    def _FROMBLOB(self, data):
        return str(data)

    def get_datatype(self, datatype):
        if datatype == "INT":
            return "INTEGER"
        if datatype in ("VARCHAR", "CHAR", "ASCII"):
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
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS {} (
                    {}_ID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT
                    , {}_INSERTED TIMESTAMP NOT NULL DEFAULT current_timestamp
                    , {}_UPDATED TIMESTAMP NOT NULL DEFAULT current_timestamp
                """.format(table.name, table.name, table.name, table.name)
                create_table_sql += ")"
                self.query(create_table_sql, squelch=True)
                self.commit()

                trigger_sql = """
                CREATE TRIGGER trigger_{}_update_timestamp AFTER UPDATE ON {}
                BEGIN
                  update {} SET {}_UPDATED = current_timestamp
                  WHERE {}_ID = NEW.{}_ID;
                END;
                """.format(table.name, table.name, table.name,
                           table.name, table.name, table.name)
                self.query(trigger_sql, squelch=True)
                self.commit()

                self.query("PRAGMA foreign_keys = 0")
                for col in table:
                    params = ()
                    sql = """
                        ALTER TABLE {}
                        ADD COLUMN {} {}
                    """.format(table.name, col.name,
                               self.get_datatype(col.datatype))
                    if col.size:
                        sql += "({})".format(str(col.size))
                    if col.required:
                        sql += " NOT NULL DEFAULT ''"
                    if col.fk_table and col.fk_col:
                        sql += """
                          REFERENCES {}({}) ON DELETE CASCADE
                         """.format(col.fk_table, col.fk_col)
                    self.query(sql, squelch=True)
                    self.commit()
                self.query("PRAGMA foreign_keys = 1")

    def create_indexes(self, indexes):
        if indexes:
            for idx in indexes:
                idx_name = "IDX_" + "_".join(idx.cols)
                idx_sql = "CREATE"
                if idx.unique:
                    idx_sql += " UNIQUE"
                idx_sql += """
                  INDEX IF NOT EXISTS {} ON {} ({})
                """.format(idx_name, idx.table, ",".join(idx.cols))
                self.query(idx_sql)

    def query(self, sql, data=None, squelch=False):
        self.rowcount = None
        self.lastrowid = None
        self.error = None
        try:
            if data:
                sql = sql.replace("%s", "?")
                result = self.cur.execute(sql, data)
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

    def next(self):
        return self.cur.fetchone()

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        self.conn.close()
