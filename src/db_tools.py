import os
import sqlite3
# Create a function that checks if db. exist. If not then initialize the db. 

class db:
    def __init__(self, name:str):
        self.name = name

    def check_if_db_exists(self):  
        _exists=os.path.exists(self.name+'.db')
        return _exists
    
    def create_db(self): 
        if self.check_if_db_exists():
            print('database {self.db_name} already exists.')
            pass

        # connect to db 
        conn = sqlite3.connect(self.name +'.db')
        cursor = conn.cursor()
        
        # scripts to execute in specific order
        script_order = [
            'create_locations_table.sql',
            'create_evseIds_table.sql',
            'create_connectorCounts_table.sql',
            'create_availabilityLog_table.sql',
            'create_availabilityAggregated_table.sql',
        ]
        for script_name in script_order: 
            with open('sql_scripts/create/' + script_name, 'r') as f:
                print(f'executing script {script_name}')
                cursor.executescript(f.read())
        conn.commit()
        conn.close()

        print(f'database {self.name} initialized as {self.name}.db')

    def insert_row(self, table_name, data_dict):
        """Insert a row into specified table"""
        
        conn = sqlite3.connect(self.name + '.db')
        cursor = conn.cursor()

        # ensures that foreign_keys are always enabled.
        cursor.execute("PRAGMA foreign_keys = ON;")
               
        try:
            # Build the INSERT statement dynamically
            columns = ', '.join(data_dict.keys())
            placeholders = ', '.join(['?' for _ in data_dict])
            values = list(data_dict.values())
            
            
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
            conn.commit()
            
            print(f"✅ Inserted row into {table_name}")
            return True, None
            
        except sqlite3.Error as e:
            print(f"❌ Error inserting into {table_name}: {e}")
            conn.rollback()
            return False, e
            
        finally:
            conn.close()