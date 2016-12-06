from data import *
import shlex, re
db = None

def init(app_db):
    global db
    db = app_db
    
def valid_value(col_type, val):
    if val == None:
        return True
    
    if col_type == "BOOL" and val in (0,1,'0','1'):
        return True

    if col_type == "INT":
        try:
            int(val)
        except: 
            return False
        return True

    if col_type == "FLOAT":
        try:
            float(val)
        except:
            return False
        return True
    
    if col_type in ("TEXT","STR","LIST"):
        return True
    
    if col_type == "DATE":
        d = re.compile("\d\d\d\d\-\d{1,2}\-\d{1,2}")
        return d.match(val)
        
    return False


class api_call:
    lists = []
    cols = {}
    query_cols = []
    search_cols = []
    order_cols = []
    udf_context = None
    udf_context_id = None
    udf_rowid = None

    def get_lists(self):
        lists = {}
        
        sql = """
        SELECT LISTS.*, LIST_ITEMS.* FROM LISTS
        JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID=LISTS_ID AND LIST_ITEMS_ENABLED=1
        """
        params = ()
        
        if self.lists or self.udf_context:
            sql += "WHERE"
            
        if self.lists:
            sql += " LISTS_NAME IN ({})".format( ",".join(('%s',) * len(self.lists)) )
            params += tuple(self.lists)
            
        if self.udf_context:
            if self.lists:
                sql += " OR "
            sql += """
            LISTS_ID IN (
            SELECT UDF_LISTS_ID 
            FROM UDF 
            WHERE
            UDF_TYPE='LIST'
            AND UDF_CONTEXT=%s
            AND UDF_CONTEXT_ID=%s
            AND UDF_ENABLED=1
            )
            """
            params += (self.udf_context, self.udf_context_id)
            
        sql += " ORDER BY LIST_ITEMS_ORDER"
        row = db.qaf(sql, params)
        while row:
            lname = row["LISTS_NAME"]
            if lname not in lists: lists[lname] = []
            lists[lname].append(dict(row))
            row = db.next()
            
        return lists
        
    def list_call(self, sql, params, meta, calc_row_function=None):
        self.udf_context_id = self.udf_context_id or 0
            
        if self.udf_context:
            context_sql = "UDF_CONTEXT=%s AND UDF_CONTEXT_ID=%s AND UDF_DATA_ROWID={} AND UDF_ENABLED=1".format(self.udf_rowid)
            context_params = (self.udf_context,self.udf_context_id)

        query = var.get("query")
        meta["query"] = query
        meta["lists"] = self.get_lists()

        sql += " WHERE 1=1"
        
        if query:
            queries = shlex.split(query)
            for query in queries:
                opreg = re.compile("([!=><])")
                qs = opreg.split(query)
                if len(qs) > 1:
                    col = qs[0]
                    op = qs[1]
                    if op == "!":
                        op = "!="
                    vals = qs[2].split("|")
                    if col in self.query_cols:
                        sql += " AND ("
                        valcount = 0
                        for val in vals:
                            if valcount > 0:
                                sql += " OR "
                                
                            if val == "NULL" and op == "=":
                                sql += "%s IS NULL" % (col,)
                            elif val == "NULL" and op == "!=":
                                sql += "%s IS NOT NULL" % (col,)
                            else:
                                sql += "{} {} %s".format(col,op)
                                params += (val,)
                            
                            valcount += 1
                            
                        sql += ")"
                    elif self.udf_context:
                        sql += " AND ("
                        valcount = 0
                        for val in vals:
                            if valcount > 0:
                                sql += " OR "
                            if val == "NULL" and op == "=":
                                sql += "("
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE {} and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1) < 1".format(context_sql)
                                sql += " OR "
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE {} and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1 and UDF_DATA_VALUE IS NULL) > 0".format(context_sql,)
                                sql += ")"
                                params += context_params + (col,) + context_params + (col,)
                            elif val == "NULL" and op == "!=":
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE {} and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1) > 0".format(context_sql)
                                params += context_params + (col,)
                            else:
                                sql += " (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE {} and UDF_ID=UDF_DATA_UDF_ID and UDF_NAME=%s and UDF_ENABLED=1 and UDF_DATA_VALUE {} %s) > 0".format(context_sql,op)
                                params += context_params + (col,val)
                            valcount += 1
                        sql += ")"
                        
                else:
                    query = "%" + query + "%"
                    sql += " AND ("
                    valcount = 0
    
                    for col in self.search_cols:
                        if valcount > 0:
                            sql += " OR "
                        sql += " {} LIKE %s ".format(col)
                        params += (query,)
                        valcount += 1
                    
                    if self.udf_context:
                        sql += " OR (SELECT COUNT(*) FROM UDF, UDF_DATA WHERE {} and UDF_ID=UDF_DATA_UDF_ID and UDF_ENABLED=1 and UDF_DATA_VALUE LIKE %s) > 0".format(context_sql)
                        params += context_params + (query,)
                    sql += ")"
                    
        if len(self.order_cols) > 0:
            sql += " ORDER BY %s" % ",".join(self.order_cols)
        
        db.query(sql,params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        row = db.next()
        rows = []
        while row:
            row = dict(row)
            if calc_row_function:
                row = calc_row_function(dict(row))
            rows.append(row)
            row = db.next()

        if self.udf_context:
            for r in rows:
                rowid = r[self.udf_rowid]
                udf_sql = """
                SELECT * FROM UDF
                LEFT OUTER JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID AND UDF_DATA_ROWID=%s
                WHERE
                UDF_CONTEXT=%s
                AND UDF_CONTEXT_ID=%s
                AND UDF_ENABLED=1
                """
                udf_params = (rowid, self.udf_context, self.udf_context_id)
                    
                db.query(udf_sql, udf_params)
                row = db.next()
                while row:
                    row = dict(row)
                    r[row["UDF_NAME"]] = row["UDF_DATA_VALUE"]
                    row = db.next()
                    
        return output(success=1, data=rows, meta=meta)
    
    def view_call(self, sql, params, meta, calc_row_function=None):
        self.udf_context_id = self.udf_context_id or 0
        meta["lists"] = self.get_lists()
                    
        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        
        if not row:
            return output(success=0, meta=meta, message="NO DATA")

        row = dict(row)
        if self.udf_context:
            udf_sql = """
            SELECT * FROM UDF
            JOIN UDF_DATA ON UDF_DATA_UDF_ID=UDF_ID
            WHERE 
            UDF_CONTEXT=%s and UDF_CONTEXT_ID=%s AND UDF_DATA_ROWID=%s
            AND UDF_ENABLED=1 
            ORDER BY UDF_ORDER
            """
            udf_params = (self.udf_context, self.udf_context_id, row[self.udf_rowid])
            db.query(udf_sql, udf_params)
            udf = db.next()
            while udf:
                row[udf["UDF_NAME"]] = udf["UDF_DATA_VALUE"]
                udf = db.next()
            
        if calc_row_function: row = calc_row_function(dict(row))
        return output(success=1, meta=meta, data=dict(row))

    def new_call(self, sql, params, meta):
        db.query(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        
        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            db.commit()
            return output(success=1, meta=meta, message="CREATED", value=db.lastrowid)
        else:
            return output(success=0, meta=meta, message="NO ROWS CREATED")            
        return None
    
    def delete_call(self, sql, params, meta):
        db.query(sql, params)
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        
        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            db.commit()
            return output(success=1, meta=meta, message="DELETED")
        else:
            return output(success=0, meta=meta, message="NO ROWS DELETED")            
        return None
    
    def save_call(self, sql, params, meta, col, val, rowid=None):
        self.udf_context_id = self.udf_context_id or 0

        if col not in self.cols:
            if self.udf_context:
                udf_sql = "SELECT * FROM UDF WHERE UDF_CONTEXT=%s and UDF_NAME=%s and UDF_CONTEXT_ID=%s"
                udf_params = (self.udf_context, col, self.udf_context_id)
                row = db.qaf(udf_sql, udf_params)
                if not row:
                    return output(success=0, meta=meta, message="INVALID COL: %s" % (col,))
                if valid_value(row["UDF_TYPE"], val):
                    udf_sql = "DELETE FROM UDF_DATA WHERE UDF_DATA_UDF_ID=%s and UDF_DATA_ROWID=%s"
                    db.query(udf_sql, (row["UDF_ID"], rowid))
                    udf_sql = "INSERT INTO UDF_DATA (UDF_DATA_UDF_ID, UDF_DATA_ROWID, UDF_DATA_VALUE) VALUES (%s,%s,%s)"
                    db.query(udf_sql, (row["UDF_ID"], rowid, val))
                    if db.error:
                        return output(success=0, meta=meta, message=db.error)
                    meta["rowcount"] = db.rowcount
                    if meta["rowcount"] > 0:
                        db.commit()
                        return output(success=1, meta=meta, message="SAVED")
                else:
                    return output(success=0, meta=meta, message="INVALID %s VALUE FOR COL (%s): %s" % (row["UDF_TYPE"], col, val))
                    
            return output(success=0, meta=meta, message="INVALID COL: %s" % (col,))
        
        col_type = self.cols[col]
        if not valid_value(col_type, val):
            return output(success=0, meta=meta, message="INVALID %s VALUE FOR COL (%s): %s" % (col_type, col, val))
        
        sql = sql.format(col)
        db.query(sql, params)
        
        if db.error:
            return output(success=0, meta=meta, message=db.error)
        
        meta["rowcount"] = db.rowcount
        if meta["rowcount"] > 0:
            db.commit()
            return output(success=1, meta=meta, message="SAVED")
        else:
            return output(success=0, meta=meta, message="NO ROWS SAVED")    