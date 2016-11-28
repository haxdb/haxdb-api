from data import *
db = None

def init(app_db):
    global db
    db = app_db
    
def valid_value(col_type, val):
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
    
    if col_type == "STR":
        return True
    
    return False


class api_call:
    lists = []
    cols = {}
    query_cols = []
    search_cols = []
    order_cols = []
    udf = False
    
    def list_call(self, sql, params, data, calc_row_function=None):
        query = var.get("query")
        include_lists = var.get("include_lists")
        data["input"]["query"] = query
        data["input"]["include_lists"] = include_lists
        if include_lists and self.lists:
            data["lists"] = {}
            
            for list_name in self.lists:
                data["lists"][list_name] = []
                list_sql = """
                SELECT * FROM LIST_ITEMS 
                JOIN LISTS ON LISTS_ID = LIST_ITEMS_LISTS_ID AND LISTS_NAME=?
                WHERE
                LIST_ITEMS_ENABLED = '1'
                ORDER BY LIST_ITEMS_ORDER
                """
                db.query(list_sql, (list_name,))
                if db.error:
                    print db.error
                    print list_sql
                row = db.next()
                while row:
                    data["lists"][list_name].append(dict(row))
                    row = db.next()
                    
        if query:
            queries = shlex.split(query)
            for query in queries:
                qs = query.split(":")
                if len(qs) > 1:
                    col = qs[0]
                    if col in self.query_cols:
                        vals = qs[1].split("|")
                        
                        sql += " AND ("
                        valcount = 0
                        for val in vals:
                            if valcount > 0:
                                sql += " OR "
                                
                            if val == "NULL":
                                sql += "%s IS NULL" % (col,)
                            else:
                                sql += "%s = ?" % (col,)
                                params += (val,)
                            
                            valcount += 1
                            
                        sql += ")"
                else:
                    sql += " AND ("
                    valcount = 0
    
                    for col in self.search_cols:
                        if valcount > 0:
                            sql += " OR "
                        sql += " %s LIKE ? " % (col,)
                        params += (query,)
                        valcount += 1
                        
                    sql += ")"
                    
        if len(self.order_cols) > 0:
            sql += " ORDER BY %s" % ",".join(self.order_cols)
        
        db.query(sql,params)
        if db.error:
            return output(success=0, data=data, message=db.error)
    
        row = db.next()
        rows = []
        while row:
            row = dict(row)
            if calc_row_function:
                row = calc_row_function(row)
            rows.append(row)
            row = db.next()
    
        return output(success=1, data=data, rows=rows)
    
    def view_call(self, sql, params, data, calc_row_function=None):
        include_lists = var.get("include_lists")
        data["input"]["include_lists"] = include_lists
        if include_lists and self.lists:
            data["lists"] = {}
            
            for list_name in self.lists:
                data["lists"][list_name] = []
                list_sql = """
                SELECT * FROM LIST_ITEMS 
                JOIN LISTS ON LISTS_ID = LIST_ITEMS_LISTS_ID AND LISTS_NAME=?
                WHERE
                LIST_ITEMS_ENABLED = '1'
                ORDER BY LIST_ITEMS_ORDER
                """
                db.query(list_sql, (list_name,))
                row = db.next()
                while row:
                    data["lists"][list_name].append(dict(row))
                    row = db.next()
                    
                    
        row = db.qaf(sql, params)
        if db.error:
            return output(success=0, data=data, message=db.error)
        
        if not row:
            return output(success=0, data=data, message="NO DATA")
        
        data["row"] = dict(row)
        if calc_row_function: 
            data["row"] = calc_row_function(data["row"])
        return output(success=1, data=data)    

    def new_call(self, sql, params, data):
        db.query(sql, params)
        if db.error:
            return output(success=0, data=data, message=db.error)
        
        data["rowcount"] = db.rowcount
        if data["rowcount"] > 0:
            db.commit()
            return output(success=1, data=data, message="DELETED")
        else:
            return output(success=0, data=data, message="NO ROWS DELETED")            
        return None
    
    def delete_call(self, sql, params, data):
        return None
    
    def save_call(self, sql, params, data, col, val):
        if col not in self.cols:
            return output(success=0, data=data, message="INVALID COL: %s" % (col,))
        
        col_type = self.cols[col]
        if not valid_value(col_type, val):
            return output(success=0, data=data, message="INVALID %s VALUE FOR COL (%s): %s" % (col_type, col, val))
        
        sql = sql % (col,)
        db.query(sql, params)
        
        if db.error:
            return output(success=0, data=data, message=db.error)
        
        data["rowcount"] = db.rowcount
        if data["rowcount"] > 0:
            db.commit()
            return output(success=1, data=data, message="SAVED")
        else:
            return output(success=0, data=data, message="NO ROWS SAVED")    