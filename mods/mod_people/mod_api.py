from flask import request, send_from_directory
from werkzeug.utils import secure_filename
import os, shlex

api = None
db = None
config = None
tools = None

valid_types = ("STATIC","TEXT","TEXTAREA","CHECKBOX","FILE","SELECT","NUMERIC","INTEGER","FLOAT","DATE","LIST")

def init(app_api, app_db, app_config, app_tools):
    global api, db, config, tools
    api = app_api
    db = app_db
    config = app_config
    tools = app_tools

def run():
    @api.app.route("/PEOPLE/list", methods=["POST","GET"])
    @api.app.route("/PEOPLE/list/<int:category>", methods=["POST","GET"])
    @api.require_auth
    @api.require_dba
    def mod_people_list(category=None):
        people_id = None
        category = category or api.data.get("category")
        query = api.data.get("query")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "list"
        data["input"]["category"] = category
        data["input"]["query"] = query

        if category:
            sql = "SELECT * FROM PEOPLE_COLUMNS WHERE "
            sql += "PEOPLE_COLUMNS_ENABLED=1 and (PEOPLE_COLUMNS_KEY=1 OR PEOPLE_COLUMNS_CATEGORY=?) "
            sql += "ORDER BY PEOPLE_COLUMNS_KEY DESC, PEOPLE_COLUMNS_ORDER"
            db.query(sql, (category,))
        else:
            sql = "SELECT * FROM PEOPLE_COLUMNS "
            sql += "WHERE PEOPLE_COLUMNS_ENABLED=1 and PEOPLE_COLUMNS_KEY=1 "            
            sql += "ORDER BY PEOPLE_COLUMNS_ORDER"
            db.query(sql)

                
        data["cols"] = []
        row = db.next()
        while row:
            col = {}
            col["name"] = row["PEOPLE_COLUMNS_NAME"]
            col["type"] = row["PEOPLE_COLUMNS_TYPE"]
            if col["type"] == "LIST":
                col["list"] = row["PEOPLE_COLUMNS_LISTS_ID"]
            
            data["cols"].append(col)
            row = db.next()
    
        if category:
            sql = """
                    SELECT * FROM LISTS
                    JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID = LISTS_ID
                    WHERE 
                    LISTS_ID IN (
                    SELECT PEOPLE_COLUMNS_LISTS_ID FROM PEOPLE_COLUMNS WHERE
                    PEOPLE_COLUMNS_TYPE = 'LIST'
                    and (PEOPLE_COLUMNS_KEY=1 OR PEOPLE_COLUMNS_CATEGORY=?)
                    and PEOPLE_COLUMNS_ENABLED = 1
                    )
                    ORDER BY LIST_ITEMS_ORDER
                    """
            db.query(sql, (category,))
              
        else:
            sql = """
                    SELECT * FROM LISTS
                    JOIN LIST_ITEMS ON LIST_ITEMS_LISTS_ID = LISTS_ID
                    WHERE 
                    LISTS_ID IN (
                    SELECT PEOPLE_COLUMNS_LISTS_ID FROM PEOPLE_COLUMNS WHERE
                    PEOPLE_COLUMNS_TYPE = 'LIST'
                    and PEOPLE_COLUMNS_KEY=1
                    and PEOPLE_COLUMNS_ENABLED = 1
                    )
                    ORDER BY LIST_ITEMS_ORDER
                    """
            db.query(sql)

        row = db.next()
        data["lists"] = {}
        while row:
            if row["LISTS_ID"] not in data["lists"]:
                data["lists"][row["LISTS_ID"]] = []
            data["lists"][row["LISTS_ID"]].append({ "value": row["LIST_ITEMS_VALUE"], "description": row["LIST_ITEMS_DESCRIPTION"] })
            row = db.next()
        
        sql = """
        SELECT * FROM PEOPLE
        JOIN PEOPLE_COLUMNS
        LEFT OUTER JOIN PEOPLE_COLUMN_VALUES ON PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PEOPLE_COLUMNS_ID and PEOPLE_COLUMN_VALUES_PEOPLE_ID = PEOPLE_ID
        WHERE
        1=1
        """
        params = ()
        
        if category:
            sql += " and (PEOPLE_COLUMNS_CATEGORY=? OR PEOPLE_COLUMNS_KEY=1)"
            params += (category,)
        else:
            sql += " and PEOPLE_COLUMNS_KEY=1"


        if query:
            queries = shlex.split(query)
            for query in queries:
                tmp = query.split(":")
                if len(tmp) > 1:
                    col = tmp[0]
                    vals = tmp[1].split("|")
                    sql += " AND ("
                    
                    valcount = 0
                    for val in vals:

                        if valcount > 0:
                            sql += " OR "
                            
                        if col == "EMAIL":
                            sql += """
                            PEOPLE_EMAIL = ?
                            """
                            params += (val,)
                        else:
                            sql += """
                            PEOPLE_ID IN (SELECT PEOPLE_COLUMN_VALUES_PEOPLE_ID FROM PEOPLE_COLUMNS JOIN PEOPLE_COLUMN_VALUES ON PEOPLE_COLUMNS_ID=PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID 
                            WHERE PEOPLE_COLUMNS_NAME=? AND PEOPLE_COLUMN_VALUES_VALUE=?)
                            """
                            params += (col,val,)

                        valcount += 1
                        
                    sql += ")"
                else:
                    query = "%" + query + "%"
                    sql += """
                    AND (
                    PEOPLE_ID IN (SELECT PEOPLE_COLUMN_VALUES_PEOPLE_ID FROM PEOPLE_COLUMN_VALUES WHERE PEOPLE_COLUMN_VALUES_VALUE LIKE ?)
                    OR
                    PEOPLE_EMAIL LIKE ?
                    )
                    """
                    params += (query,query,)


        db.query(sql, params)
            
        if db.error:
            return api.output(success=0, data=data, message=db.error)
        
        row = db.next()
        rows = {}
        while row:
            if row["PEOPLE_ID"] not in rows:
                rows[row["PEOPLE_ID"]] = {}
                
            rows[row["PEOPLE_ID"]][row["PEOPLE_COLUMNS_NAME"]] = row["PEOPLE_COLUMN_VALUES_VALUE"]
            rows[row["PEOPLE_ID"]]["EMAIL"] = row["PEOPLE_EMAIL"]
            rows[row["PEOPLE_ID"]]["DBA"] = row["PEOPLE_DBA"]
            row = db.next()
        tmp = rows
        rows = []
        for pid in tmp.keys():
            tmp[pid]["PEOPLE_ID"] = pid
            rows.append(tmp[pid])

        return api.output(success=1, data=data, rows=rows)
            


    @api.app.route("/PEOPLE/save", methods=["GET","POST"])
    @api.app.route("/PEOPLE/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_save(rowid=None,col=None,val=None):
        table_cols = { "EMAIL": "PEOPLE_EMAIL", "DBA": "PEOPLE_DBA" }
        
        rowid = rowid or api.data.get("rowid")
        column = col or api.data.get("col")
        value = val or api.data.get("val")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = column
        data["input"]["val"] = value
        data["oid"] = "PEOPLE-%s-%s" % (rowid,column)
        
        if column in table_cols:
            sql = "UPDATE PEOPLE SET %s=? WHERE PEOPLE_ID=?" % table_cols[column]
            db.query(sql,(value, rowid))

        else:
            col = tools.get_col_definition(col_name=column)
            if not col:
                return api.output(success=0, message="INVALID VALUE: col", data=data)
            
            col_name = col["PEOPLE_COLUMNS_NAME"]
            col_type = col["PEOPLE_COLUMNS_TYPE"]
            defid = col["PEOPLE_COLUMNS_ID"]
            
            if col_type == "FILE":
                #check file
                pass
            elif not tools.valid_col_value(col_name,col_type,value):
                return api.output(success=0, message="INVALID VALUE: val", data=data)
            
    
            if col_type == "FILE":
                if 'value' not in request.files:
                    return api.output(success=0, message="NO FILE UPLOADED")
                
                f = request.files["value"]
                if f.filename == '':
                    return api.output(success=0, message="UPLOAD CANCELLED", data=data)
                
                #filename = secure_filename(file.filename)
                fname, fext = os.path.splitext(f.filename)
                keycols = tools.get_keycols(rowid)
                filename = secure_filename("PEOPLE." + str(rowid) + "." + ".".join(keycols) + "." + column + fext)
                f.save(os.path.join(config["API"]["UPLOADS"], filename))
                value = filename
    
            sql = "DELETE FROM PEOPLE_COLUMN_VALUES WHERE PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID=? and PEOPLE_COLUMN_VALUES_PEOPLE_ID=?"
            db.query(sql,(defid, rowid))
            db.rowcount = 0
            sql = "INSERT INTO PEOPLE_COLUMN_VALUES (PEOPLE_COLUMN_VALUES_PEOPLE_ID,PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID,PEOPLE_COLUMN_VALUES_VALUE) VALUES (?,?,?)"
            db.query(sql,(rowid, defid, value))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, message="SAVED", data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)

    @api.app.route("/PEOPLE/download", methods=["GET","POST"])
    @api.app.route("/PEOPLE/download/<int:rowid>/<col>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_download(rowid=None,col=None):
        rowid = rowid or api.data.get("rowid")
        column = col or api.data.get("col")
        
        sql = """SELECT * FROM PEOPLE
        JOIN PEOPLE_COLUMNS ON PEOPLE_COLUMNS_NAME=?
        JOIN PEOPLE_COLUMN_VALUES ON PEOPLE_COLUMN_VALUES_PEOPLE_COLUMNS_ID = PEOPLE_COLUMNS_ID and PEOPLE_COLUMN_VALUES_PEOPLE_ID=PEOPLE_ID
        WHERE PEOPLE_ID=?
        """
        db.query(sql,(column,rowid,))
        row = db.next()
        
        print rowid, column, row
        
        if row:
            f = row["PEOPLE_COLUMN_VALUES_VALUE"]
            return send_from_directory(directory=config["API"]["UPLOADS"], filename=f, as_attachment=True)
        return False
    
    @api.app.route("/PEOPLE/new", methods=["GET","POST"])
    @api.app.route("/PEOPLE/new/<email>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_new(email=None):
        email = email or api.data.get("email")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "new"
        data["input"]["email"] = email

        if not email:
            return api.output(success=0, message="MISSING INPUT: email", data=data)

        sql = "INSERT INTO PEOPLE (PEOPLE_EMAIL,PEOPLE_DBA) VALUES (?,0)"
        db.query(sql,(email,))

        if db.rowcount > 0:
            data["rowid"] = db.lastrowid
            db.commit()
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)
    
    @api.app.route("/PEOPLE/delete/", methods=["GET","POST"])
    @api.app.route("/PEOPLE/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")
        
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        if not rowid:
            return api.output(success=0, message="MISSING INPUT: rowid", data=data)
        
        sql = "DELETE FROM PEOPLE WHERE PEOPLE_ID = ?"
        db.query(sql,(rowid,))

        if db.rowcount > 0:
            db.commit();
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)
    
    
    @api.app.route("/PEOPLE_COLUMNS/list", methods=["POST","GET"])
    @api.require_auth
    @api.require_dba
    def mod_people_columns_list():
        query = api.data.get("query")
 
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_COLUMNS"
        data["input"]["action"] = "list"
        data["input"]["query"] = query
        
        rows = {}
        if query:
            query = "%" + query + "%"
            sql = "SELECT * FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_CATEGORY LIKE ? OR PEOPLE_COLUMNS_NAME LIKE ? ORDER BY PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_NAME"
            db.query(sql, (query, query,))
        else:
            sql = "SELECT * FROM PEOPLE_COLUMNS ORDER BY PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_NAME"
            db.query(sql)
        row = db.next()
        while row:
            rows[row["PEOPLE_COLUMNS_ID"]] = dict(row)
            row = db.next()
            
        return api.output(success=1, rows=rows, data=data)

    @api.app.route("/PEOPLE_COLUMNS/categories", methods=["POST","GET"])
    @api.require_auth
    @api.require_dba
    def mod_people_list_categories():
        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_COLUMNS"
        data["input"]["action"] = "categories"
        data["categories"] = []

        sql = "SELECT DISTINCT PEOPLE_COLUMNS_CATEGORY FROM PEOPLE_COLUMNS ORDER BY PEOPLE_COLUMNS_ORDER,  PEOPLE_COLUMNS_NAME"
        db.query(sql)
        row = db.next()
        while row:
            data["categories"].append(row["PEOPLE_COLUMNS_CATEGORY"])
            row = db.next()
            
        return api.output(success=1, data=data)
    
    @api.app.route("/PEOPLE_COLUMNS/save", methods=["GET","POST"])
    @api.app.route("/PEOPLE_COLUMNS/save/<int:rowid>/<col>/<val>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_PEOPLE_COLUMNS_save(rowid=None,col=None,val=None):
        rowid = rowid or api.data.get("rowid")
        column = col or api.data.get("col")
        value = val or api.data.get("val")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_COLUMNS"
        data["input"]["action"] = "save"
        data["input"]["rowid"] = rowid
        data["input"]["col"] = column
        data["input"]["val"] = value
        data["oid"] = "PEOPLE_COLUMNS-%s-%s" % (rowid,column,)
        
        if not rowid:
            return api.output(success=0, message="MISSING INPUT: rowid", data=data)
        
        if not column:
            return api.output(success=0, message="MISSING INPUT: col", data=data)
        
        valid_columns = (
            "PEOPLE_COLUMNS_NAME",
            "PEOPLE_COLUMNS_ENABLED",
            "PEOPLE_COLUMNS_ORDER",
            "PEOPLE_COLUMNS_TYPE",
            "PEOPLE_COLUMNS_LISTS_ID",
            "PEOPLE_COLUMNS_KEY",
            "PEOPLE_COLUMNS_CATEGORY",
            "PEOPLE_COLUMNS_DEFAULT",
        )
        
        valid_internal = (
            "PEOPLE_COLUMNS_KEY",
            "PEOPLE_COLUMNS_ORDER",
            "PEOPLE_COLUMNS_CATEGORY",
        )
        
        if column == "PEOPLE_COLUMNS_NAME" and value:
            value = value.replace(" ","_")
            
        if column not in valid_columns:
            return api.output(success=0, message="INVALID VALUE: col", data=data)
        
        if column in ("PEOPLE_COLUMNS_ENABLED","PEOPLE_COLUMNS_KEY") and int(value) not in (0,1):
            return api.output(success=0, message="INVALID VALUE: val", data=data)
        
        if column == "PEOPLE_COLUMNS_ORDER":
            try:
                int(value)
            except ValueError:
                return api.output(success=0, message="INVALID VALUE: val", data=data)
            
        if column == "PEOPLE_COLUMNS_TYPE" and value not in valid_types:
            return api.output(success=0, message="INVALID VALUE: val", data=data)
        
        if column in valid_internal:
            sql = "UPDATE PEOPLE_COLUMNS SET %s = ? WHERE PEOPLE_COLUMNS_ID=?" % column
        else:
            sql = "UPDATE PEOPLE_COLUMNS SET %s = ? WHERE PEOPLE_COLUMNS_ID=? AND (PEOPLE_COLUMNS_INTERNAL IS NULL OR PEOPLE_COLUMNS_INTERNAL != 1)" % column
        db.query(sql,(value, rowid))
 
        if db.rowcount > 0:
            db.commit()
            return api.output(success=1, message="SAVED", data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNABLE TO CHANGE INTERNAL DATA", data=data)
        
    @api.app.route("/PEOPLE_COLUMNS/new", methods=["GET","POST"])
    @api.app.route("/PEOPLE_COLUMNS/new/<name>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_columns_new(name=None):
        sname = name or api.data.get("name")
        senabled = api.data.get("enabled") or 0
        sorder = api.data.get("order") or 999
        stype = api.data.get("type") or "TEXT"
        skey = api.data.get("key") or 0
        scategory = api.data.get("category") or "NEW CATEGORY"
        
        if not sname:
            return api.output(success=0, message="MISSING INPUT: name")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_COLUMNS"
        data["input"]["action"] = "new"
        data["input"]["name"] = sname
        data["input"]["enabled"] = senabled
        data["input"]["order"] = sorder
        data["input"]["skey"] = skey
        data["input"]["category"] = scategory
        
        sname = sname.replace(" ","_")
        try:
            int(sorder)
        except ValueError:
            return api.output(success=0, message="INVALID VALUE: order", data=data)
        
        if int(senabled) not in (0,1):
            return api.output(success=0, message="INVALID VALUE: enabled", data=data)

        if int(skey) not in (0,1):
            return api.output(success=0, message="INVALID VALUE: key", data=data)
        
        if stype not in valid_types:
            return api.output(success=0, message="INVALID VALUE: type", data=data)
        
        sql = "INSERT INTO PEOPLE_COLUMNS (PEOPLE_COLUMNS_NAME, PEOPLE_COLUMNS_ENABLED, PEOPLE_COLUMNS_ORDER, PEOPLE_COLUMNS_TYPE, PEOPLE_COLUMNS_KEY, PEOPLE_COLUMNS_CATEGORY, PEOPLE_COLUMNS_INTERNAL) VALUES (?,?,?,?,?,?,0)"
        db.query(sql,(sname,senabled,sorder,stype,skey,scategory,))

        if db.rowcount > 0:
            data["rowid"] = db.lastrowid
            db.commit();
            sql = "SELECT * FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_ID=?"
            db.query(sql, (data["rowid"],))
            data["row"] = dict(db.next())
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)
    
    @api.app.route("/PEOPLE_COLUMNS/delete", methods=["GET","POST"])
    @api.app.route("/PEOPLE_COLUMNS/delete/<int:rowid>", methods=["GET","POST"])
    @api.require_auth
    @api.require_dba
    @api.no_readonly
    def mod_people_columns_delete(rowid=None):
        rowid = rowid or api.data.get("rowid")

        data = {}
        data["input"] = {}
        data["input"]["api"] = "PEOPLE_COLUMNS"
        data["input"]["action"] = "delete"
        data["input"]["rowid"] = rowid
        
        if not rowid:
            return api.output(success=0, message="MISSING INPUT: rowid", data=data)

        
        sql = "DELETE FROM PEOPLE_COLUMNS WHERE PEOPLE_COLUMNS_ID = ?"
        db.query(sql,(rowid,))

        if db.rowcount > 0:
            db.commit();
            return api.output(success=1, data=data)
        
        if db.error:
            return api.output(success=0, message=db.error, data=data)
        
        return api.output(success=0, message="UNKNOWN ERROR", data=data)        
