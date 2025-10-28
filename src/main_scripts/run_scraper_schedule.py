from scrapers.with_requests.scrape_availability_with_api import scraper as avail_scraper
from scrapers.with_requests.scrape_locations_with_api import scraper as loc_scraper 

from db_tools import db
from logging_config import setup_logging

import schedule
import os
import time
import logging
from datetime import datetime 

# Get logger for this module
logger = logging.getLogger(__name__)

def run_avail(speed): 
    logger.info(f"Starting availability scrape for speed: {speed}")
    
    # create database connection
    database = db(
        name='./data/db/charging'
    )
    database.create_db()

    # get locationIds
    locids=database.select_locationIds_by_speed(speed=speed)
    logger.info(f"Found {len(locids)} locations for speed: {speed}")

    # setup scraper
    availability_scraper=avail_scraper(
        keyword='availability',
        identifiers=locids,
        url_re='https://clever.dk/api/chargers/location/{}',
        out_path='./data/',
        save_json = False,
    )

    # run scraper
    logger.info("Running availability scraper")
    availability_scraper.run(max_workers=2)
    availability = availability_scraper.results
    logger.info(f"Scraping completed. Processing {len(availability)} results")
    
    # adding counter to track number of succesfully inserted rows.
    ntotalsuccess = 0
    ntotalplugs = 0 
    for locationId in availability.keys():
        v = availability[locationId]['data']
        nlocsuccess, nplugs=database.insert_row_in_availabilityLog_table(loc_avail_query=v)
        ntotalsuccess += nlocsuccess
        ntotalplugs += nplugs
    
    logger.info(f"Availability db-insertion completed for speed: {speed}, Inserted {ntotalsuccess} rows. Found ids for {ntotalplugs} plugs.")


def run_locations():
    logger.info("Starting locations scrape")
    
    locations_scraper=loc_scraper(
        keyword='locations',
        identifiers=['locations'],
        url_re='https://clever.dk/api/chargers/locations',
        out_path='./data/',
        save_json = False,
    )

    # Query
    locations_scraper.run(max_workers = 1)
    locations = locations_scraper.results
    locations=locations[locations_scraper.identifiers[0]]
    logger.info(f"Retrieved {len(locations)} locations")
    
    # Insert into database: 
    database=db(name='./data/db/charging')
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

    logger.info(f'For {nmissing_ConnectorCounts} locations "connectorCounts" did not exist. Used "plugTypes" instead.')
    logger.info("Locations scrape completed")



if __name__ == "__main__":
    # Initialize logging FIRST, before any other code runs
    setup_logging()
    
    logger.info("="*60)
    logger.info("Scraper Application Starting")
    logger.info("="*60)
    
    run_mode = os.environ.get('RUN_MODE', 'once') # defaults to 'once if RUN_MODE does not exist

    # On startup always populate locations table, and initialize database if it does not exist
    run_locations()

    if run_mode == 'scheduled':
        logger.info('Initializing run schedule')
        """SET THE SCHEDULING HERE"""
        standard_minute_interval = int(os.environ.get('standard_minute_interval'))
        fast_minute_interval=int(os.environ.get('fast_minute_interval'))
        rapid_minute_interval=int(os.environ.get('rapid_minute_interval'))
        location_day_interval=int(os.environ.get('location_day_interval'))

        logger.info(f"Schedule configuration:")
        logger.info(f"  - Standard: every {standard_minute_interval} minutes")
        logger.info(f"  - Fast: every {fast_minute_interval} minutes")
        logger.info(f"  - Rapid: every {rapid_minute_interval} minutes")
        logger.info(f"  - Locations: every {location_day_interval} days")

        # Set the schedule - availability: 
        schedule.every(standard_minute_interval).minutes.do(run_avail, speed='Standard')
        schedule.every(fast_minute_interval).minutes.do(run_avail, speed='Fast')
        schedule.every(rapid_minute_interval).minutes.do(run_avail, speed='Rapid')

        # set the schedule - locations
        schedule.every(location_day_interval).days.do(run_locations)

        logger.info("Schedule initialized. Starting scheduled execution loop")

        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every x seconds
            
    else:
        logger.info(f"Running scrapers once.")
        run_avail(speed='Standard')
        run_avail(speed='Fast')
        run_avail(speed='Rapid')