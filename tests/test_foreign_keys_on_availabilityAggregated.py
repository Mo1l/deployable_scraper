from db_tools import db

# Setup test db. 
test_db=db(name='test')
test_db.create_db()

# Populating test db. 
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


## Inserting connectorCounts into db.
connector_count_insert = {
    'locationId': 'ABC',
    'revision': 1, 
    'chargingGroup': 1, 
}
test_db.insert_row('connectorCounts', connector_count_insert)


## insert create_availabilityAggregated_table with right parameters
availability_agg_insert = {
    'locationId': 'ABC',
    'revision': 1, 
    'chargingGroup': 1, 
    'availableCount': 1,
    'totalCount': 2,
    'createdAtTime': 100
}
success, error=test_db.insert_row('availabilityAggregated', availability_agg_insert)

assert success, 'Could not insert correct data into AvailabilityLog'

## insert create_availabilityAggregated_table with wrong parameters
wrong_availability_agg_insert = {
    'locationId': 'ABC',
    'revision': 1, 
    'chargingGroup': 9999, 
    'availableCount': 1,
    'totalCount': 2,
    'createdAtTime': 100
}


success, error=test_db.insert_row('availabilityAggregated', wrong_availability_agg_insert)


try:
    assert error.sqlite_errorcode == 787, 'sqlite does not return 787 error when inserting non existing evseId'
except: 
    raise AssertionError('assert statement could not be evaluated.')
