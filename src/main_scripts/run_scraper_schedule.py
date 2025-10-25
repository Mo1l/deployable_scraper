from scrapers.with_requests.scrape_availability_with_api import scraper 
from db_tools import db
import schedule
import os
import time
from datetime import datetime 

def run_avail(speed): 
    # create database connection
    database = db(
        name='charging'
    )
    database.create_db()

    # get locationIds
    locids=database.select_locationIds_by_speed(speed=speed)

    # setup scraper
    availability_scraper=scraper(
        keyword='availability',
        identifiers=locids,
        url_re='https://clever.dk/api/chargers/location/{}',
        out_path='./data/',
    )

    # run scraper
    availability_scraper.run(max_workers=2)
    availability = availability_scraper.results

    for locationId in availability.keys():
        v = availability[locationId]['data']
        database.insert_row_in_availabilityLog_table(loc_avail_query=v)


def run_locs():
    locations_scraper=scraper(
        keyword='locations',
        identifiers=['locations'],
        url_re='https://clever.dk/api/chargers/locations',
        out_path='./data/',
    )

    # Query
    locations_scraper.run(max_workers = 1)
    locations = locations_scraper.results
    locations=locations[locations_scraper.identifiers[0]] 
    # Insert into database: 
    database=db(name='charging')
    database.create_db()

    nmissing_ConnectorCounts = 0
    for locationId in locations.keys():
        v = locations[locationId]
        # insert into locations table
        database.insert_row_in_locations_table(v)

        # insert into connectorGroup table
        try: 
            connector_dict = v['connectorCounts']
        except KeyError:
            connector_dict = v['plugTypes']
            nmissing_ConnectorCounts += 1

        for connectorGroup, connectorCount in enumerate(connector_dict):  
            database.insert_row_in_connectorGroup_table(
                location=v, 
                connectorGroup=connectorGroup, 
                connectorCount=connectorCount,
            )

    print(f'for {nmissing_ConnectorCounts} locations "connectorCounts" did not exist. Used "plugTypes" instead.')



if __name__ == "__main__":
    run_mode = os.environ.get('RUN_MODE', 'once') # defaults to 'once if RUN_MODE does not exist

    # On startup always populate locations table, and initialize database if it does not exist
    run_locs()

    if run_mode == 'scheduled':
        print('Initializing run schedule')
        """SET THE SCHEDULING HERE"""
        standard_minute_interval = int(os.environ.get('standard_minute_interval'))
        fast_minute_interval=int(os.environ.get('fast_minute_interval'))
        rapid_minute_interval=int(os.environ.get('rapid_minute_interval'))

        # Set the schedule - availability: 
        schedule.every(standard_minute_interval).minutes.do(run_avail, speed='Standard')
        schedule.every(fast_minute_interval).minutes.do(run_avail, speed='Fast')
        schedule.every(rapid_minute_interval).minutes.do(run_avail, speed='Rapid')

        # set the schedule - locations
        schedule.every(7).days.do(run_locs)

        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every x seconds
            
    else:
        print('Running the scraper once')
        run_avail(speed='Standard')
        run_avail(speed='Fast')
        run_avail(speed='Rapid')