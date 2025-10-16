import os
import sqlite3
# Create a function that checks if db. exist. If not then initialize the db. 

class db_tools:
    def __init__():
        pass 

    def check_if_db_exists(self):  
        _exists=os.path.exists(self.db_name)
        return _exists
    
    def create_db(self): 
        if self.check_if_db_exists():
            print('database {self.db_name} already exists.')
            pass

        # connect to db 
        conn = sqlite3.connect(self.db_name)
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
                cursor.executescript(f.read())
        conn.commit()
        conn.close()

        print(f'database {self.db_name} initialized as {self.db_name}.db')

