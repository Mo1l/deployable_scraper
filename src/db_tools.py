import os
import sqlite3
import logging
from importlib import resources

# Create module-level logger
logger = logging.getLogger(__name__)

class db:
    def __init__(self, name:str):
        self.name = name

    def check_if_db_exists(self):  
        _exists=os.path.exists(f'{self.name}.db')
        return _exists
    
    def create_db(self): 
        if self.check_if_db_exists():
            logger.debug(f"Database {self.name} already exists, skipping creation")
            return 

        logger.debug(f"Creating database: {self.name}")
        
        # connect to db 
        conn = sqlite3.connect(f'{self.name}.db')
        cursor = conn.cursor()
        
        # scripts to execute in specific order
        script_order = [
            'create_locations_table.sql',
            'create_evseIds_table.sql',
            'create_connectorGroups_table.sql',
            'create_availabilityLog_table.sql',
            'create_availabilityAggregated_table.sql',
            'create_latest_connectorGroups_newest_revision_view.sql',
        ]

        for script_name in script_order: 
            logger.debug(f"Executing script: {script_name}")
            sql_script = resources.read_text('sql_scripts.create', script_name)
            cursor.executescript(sql_script)
        conn.commit()
        conn.close()

        logger.info(f"Database initialized successfully at {self.name}.db")

    def insert_row(self, table_name, row_dict):
        """Insert a row into specified table"""
        
        conn = sqlite3.connect(f'{self.name}.db')
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
            
            logger.debug(f"✅ Successfully inserted row into {table_name}")

            return True, None
            
        except sqlite3.Error as e:
            logger.debug(f"❌ Error inserting into {table_name}: {e}", exc_info=True)

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
        connectors = evse.get('connectors', {})
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
        evses = loc_avail_query.get('availability', {}).get('evses', {})
        evses_pluginfo = loc_avail_query.get('evses')
        nplugs = len(evses_pluginfo.keys())
        # now we want to loop over all the evses
        
        # XXX: This skips any stations where there is no availability data.
        # TODO: Add logging if this if this occurs. That is if there is no availability data.
        if len(evses.keys()) == 0: 
            logger.warning(
                "No availability data for locationId=%s",
                loc_avail_query.get('locationId'),
            )
        
        # keep count of successes: 
        nsuccess = 0
        for evse_key in evses.keys():
            try:
                evse = evses.get(evse_key)
                evse_pluginfo=evses_pluginfo.get(evse_key, {})
                
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
                
                # add to nsuccess
                nsuccess += int(success)

            except AttributeError as e:
                logger.warning(
                    'AttributeError for locationId=%s, evseId=%s',
                    loc_avail_query.get('locationId'),
                    evse_key,
                    exc_info=True)
                continue
        return nsuccess, nplugs

    def select_locationIds_by_speed(self, speed:str):
        """Get locationIds with specific speed (latest revision only)"""
        
        logger.debug(f"Selecting locationIds for speed: {speed}")

        sql_script=resources.read_text('sql_scripts.select', 'select_locationIds_by_plugType.sql')

        conn = sqlite3.connect(f'{self.name}.db')
        cursor = conn.cursor()
        try:
            cursor.execute(sql_script, (speed,))
            results = cursor.fetchall()
        except:
            pass
        
        finally: 
            conn.close()
        
        return [row[0] for row in results]  # Extract locationIds
