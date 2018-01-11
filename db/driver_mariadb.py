import mysql.connector as mariadb


class db:

    logger = None

    def __init__(self, config, logger):
        self.logger = logger
        self.conn = mariadb.connect(host=config["HOST"],
                                    port=config["PORT"],
                                    user=config["USER"],
                                    password=config["PASS"],
                                    database=config["DB"])
        self.cur = self.conn.cursor(dictionary=True)

    def _TOBLOB(self, filedata):
        return filedata

    def _FROMBLOB(self, filedata):
        return filedata

    def get_datatype(self, datatype, datasize):
        if datasize:
            datasize = int(datasize)

        if datatype == "INT":
            if datasize:
                return "INT({})".format(datasize)
            return "INT"

        if datatype == "CHAR":
            if datasize:
                return "VARCHAR({})".format(datasize)
            return "VARCHAR(50)"

        if datatype == "BOOL":
            return "INT(1)"

        if datatype == "FLOAT":
            if datasize:
                return "FLOAT({},4)".format(datasize)
            return "FLOAT(10,4)"

        if datatype == "TEXT":
            return "TEXT"

        if datatype == "BLOB":
            return "MEDIUMBLOB"

        if datatype == "DATETIME":
            return "INTEGER"

    def create(self, tables=None, indexes=None):
        self.create_tables(tables)
        self.create_indexes(indexes)

    def create_tables(self, tables):
        if tables:
            for table in tables:
                t_sql = """
                CREATE TABLE IF NOT EXISTS {} (
                {}_ID INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
                {}_INTERNAL INT(1) NOT NULL DEFAULT 0,
                {}_INSERTED TIMESTAMP NOT NULL DEFAULT '0000-00-00 00:00:00',
                {}_UPDATED TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                                              ON UPDATE CURRENT_TIMESTAMP
                )""".format(table.name, table.name, table.name,
                            table.name, table.name)
                self.query(t_sql, squelch=True)
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
                    sql = """
                    ALTER TABLE {} ADD COLUMN {} {}
                    """.format(table.name, col.name,
                               self.get_datatype(col.datatype, col.size))
                    if col.required:
                        sql += " NOT NULL"
                    self.query(sql, squelch=True)

                    if col.fk_table and col.fk_col:
                        sql = """
                        ALTER TABLE {} ADD CONSTRAINT fk_{}_{} FOREIGN KEY ({})
                                           REFERENCES {}({}) ON DELETE CASCADE
                        """.format(table.name, table.name, col.name,
                                   col.name, col.fk_table, col.fk_col)
                        self.query(sql, squelch=True)

                    self.commit()
                self.query("SET FOREIGN_KEY_CHECKS=1")

    def create_indexes(self, indexes):
        if indexes:
            for idx in indexes:
                idx_name = "IDX_" + "_".join(idx.cols)
                idx_sql = "CREATE"
                if idx.unique:
                    idx_sql += " UNIQUE"
                idx_sql += " INDEX {} ON {} ({})".format(idx_name,
                                                         idx.table,
                                                         ",".join(idx.cols))
                self.query(idx_sql, squelch=True)

    def query(self, sql, data=None, squelch=False):
        self.rowcount = None
        self.lastrowid = None
        self.error = None

        try:
            if data:
                result = self.cur.execute(sql, data)
            else:
                result = self.cur.execute(sql)
            self.rowcount = self.cur.rowcount
            self.lastrowid = self.cur.lastrowid
            return result
        except mariadb.Error as error:
            self.error = str(error)
            if not squelch:
                self.logger.warn("\n#######################################\n")
                self.logger.warn("SQL ERROR: %s" % self.error)
                self.logger.warn(data)
                self.logger.warn("-----------------------------------")
                self.logger.warn(sql)
                self.logger.warn("\n#######################################\n")

    def next(self):
        return self.cur.fetchone()

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def close(self):
        self.conn.close()
