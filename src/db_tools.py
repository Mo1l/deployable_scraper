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
            'create_connectorGroups_table.sql',
            'create_availabilityLog_table.sql',
            'create_availabilityAggregated_table.sql',
        ]
        breakpoint()
        for script_name in script_order: 
            with open('sql_scripts/create/' + script_name, 'r') as f:
                print(f'executing script {script_name}')
                cursor.executescript(f.read())
        conn.commit()
        conn.close()

        print(f'database {self.name} initialized as {self.name}.db')

    def insert_row(self, table_name, row_dict):
        """Insert a row into specified table"""
        
        conn = sqlite3.connect(self.name + '.db')
        cursor = conn.cursor()

        # ensures that foreign_keys are always enabled.
        cursor.execute("PRAGMA foreign_keys = ON;")
               
        try:
            # Build the INSERT statement dynamically
            columns = ', '.join(row_dict.keys())
            placeholders = ', '.join(['?' for _ in row_dict])
            values = list(row_dict.values())
            
            
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

    def insert_row_in_locations_table(self, location):
        # adding these to ensure that if there is ever a case v_coords coordinates or timestamp does not exist then
        # we can still call with get and get nan values
        location_coords = location.get('coordinates', {})
        location_timestamp = location.get('timestamp', {})
        
        data_row = {
            'locationId': location.get('locationId') ,
            'revision': location.get('revision'), 
            'name': location.get('name'),
            'partnerStatus': location.get('partnerStatus'),
            'isRoamingPartner': location.get('isRoamingPartner'),
            'origin': location.get('origin'),
            'coords_lat': location_coords.get('lat'),
            'coords_lng': location_coords.get('lng'),
            'ts_seconds': location_timestamp.get('seconds'),
            'ts_nanoseconds': location_timestamp.get('nanoseconds'),
        }
        
        self.insert_row('locations', row_dict=data_row)

    def insert_row_in_connectorGroup_table(self, location:dict, connectorGroup:int, connectorCount:dict):

        data_row = {
            'locationId': location.get('locationId') ,
            'revision': location.get('revision'), 
            'connectorGroup': connectorGroup,
            'plugType': connectorCount.get('plugType'), 
            'speed': connectorCount.get('speed'),
            'count': connectorCount.get('count'),
        }
        
        success, error=self.insert_row('connectorGroups', row_dict=data_row)

        return success, error


    def insert_row_in_evseIds_table(self, location, evse:dict): 
        """
        The evse object is a dict and is a value returned from the 'evses' object. 
        """
        connectors = evse['connectors']
        for evseConnectorId in connectors.keys():
            # I expect there is only one ky in connectors but if there is more I should get an unique error.
            plug_info=connectors[evseConnectorId]

            data_row = {
            'locationId': location.get('locationId', 'returnsError'),
            'revision': location.get('revision', 'returnsError'),
            'evseId': evse.get('evseId', 'returnsError'),
            'isRoamingPartner': location.get('isRoamingPartner'),
            'isRoamingAllowed': location.get('publicAccess',{}).get('isRoamingAllowed'),
            'visibility': location.get('visibility'),
            'vendorName': evse.get('vendorName'),
            'evseConnectorId': plug_info.get('evseConnectorId'), 
            'plugType': plug_info.get('plugType'), 
            'powerType': plug_info.get('powerType'),
            'maxPowerKw': plug_info.get('maxPowerKw'),
            'connectorId': plug_info.get('connectorId'),
            'speed': plug_info.get('speed'),
            }
            success, error=self.insert_row(table_name='evseIds', row_dict=data_row)

    def insert_row_in_availabilityLog_table(self, loc_avail_query):
        evses = loc_avail_query.get('availability', {}).get('evses')
        evses_pluginfo = loc_avail_query.get('evses')
        # now we want to loop over all the evses
        for evse_key in evses.keys():
            evse = evses.get(evse_key)
            evse_pluginfo=evses_pluginfo.get(evse_key)
            
            # Construct a data row
            data_row = {
            'locationId': loc_avail_query.get('locationId', 'returnsError'),
            'revision': loc_avail_query.get('revision', 'returnsError'),
            'evseId': evse.get('evseId', 'returnsError'),
            'status': evse.get('status', 'returnsNoError'),
            'timestamp': evse.get('timestamp')
            }
            success = False
            success, error=self.insert_row('availabilityLog', row_dict=data_row)

            if (not success) and (error.sqlite_errorcode == 787):
                self.insert_row_in_evseIds_table(location=loc_avail_query, evse=evse_pluginfo)
                success, error=self.insert_row('availabilityLog', row_dict=data_row)

    def get_chargerIds_by_type(self, charger_type:str):
        pass # has to be created
