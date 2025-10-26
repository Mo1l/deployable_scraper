from test_tools import test_db as db

def test_foreign_keys_on_availabilityLog():
    try:
        test_db=db(name='test')

        test_db.create_db()

        ## Inserting locations into db.
        loc_insert = {
            'locationId': 'ABC',
            'revision': 1,
            'name': 'test',
            'partnerStatus': 'No' ,
            'isRoamingPartner': True,
            'origin': 'something' ,
            'coords_lat': 3.10 ,
            'coords_lng': 1.28 ,
            'ts_seconds':  100,
            'ts_nanoseconds': 200,
        }
        test_db.insert_row('locations', loc_insert)

        ## Inserting evseids into db.
        evse_insert = {
            'locationId': 'ABC',
            'revision': 1,
            'evseId': '1',
        }
        test_db.insert_row('evseids', evse_insert)

        ## insert create_availabilityLog_table with right parameters
        availability_log_insert = {
            'locationId': 'ABC',
            'revision': 1,
            'evseId': '1',
            'status': 'Available',
            'timestamp': 100
        }
        success, error=test_db.insert_row('availabilityLog', availability_log_insert)

        assert success, 'Could not insert correct data into AvailabilityLog'

        ## insert create_availabilityLog_table with wrong parameters
        wrong_availability_log_insert = {
            'locationId': 'ABC',
            'revision': 1,
            'evseId': '9999',
            # missing connectorId and status
            'timestamp': 100
        }
        success, error=test_db.insert_row('availabilityLog', wrong_availability_log_insert)

        assert error.sqlite_errorcode == 787, 'sqlite does not return 787 error when inserting non existing evseId'
    
    finally:
        test_db.clean_up_db()

if __name__ == '__main__':
    test_foreign_keys_on_availabilityLog()
