
class col:
    name = None
    datatype = None
    size = None
    required = None
    fk_table = None
    fk_col = None
    
    def __init__(self, name, datatype, size=None, required=False, fk_table=None, fk_col=None):
        self.name = name
        self.datatype = datatype
        self.size = size
        self.required = required
        self.fk_table = fk_table
        self.fk_col = fk_col

class index:
    table = None
    cols = []
    unique = False
    
    def __init__(self, table, cols, unique=False):
        self.table = table
        self.cols = cols
        self.unique = unique
     
    def __iter__(self):
        return iter(self.cols)
     
class table:
    name = None
    cols = []
    indexes = []
    
    def __init__(self, name):
        self.name = name
        self.cols = []
        self.indexes = []
    
    def __iter__(self):
        return iter(self.cols)
    
    def add(self, col_name, col_type, col_size=None, col_required=False, fk_table=None, fk_col=None):
        self.add_col(col(col_name, col_type, col_size, col_required, fk_table, fk_col))
        
    def add_col (self, col):
        self.cols.append(col)
        
    def add_index (self, idx):
        self.indexes.append(idx)
    
        