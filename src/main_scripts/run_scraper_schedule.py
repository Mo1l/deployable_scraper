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

def run_avail(speed:str, max_workers:int): 
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
    availability_scraper.run(max_workers=max_workers)
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
    

    # On startup always populate locations table, and initialize database if it does not exist
    run_locations()

    # retrieving scraper settings
    speed = os.environ.get('SCRAPER_TYPE').capitalize()
    minute_interval=int(os.environ.get('MINUTE_INTERVAL'))
    location_day_interval=int(os.environ.get('LOCATION_DAY_INTERVAL'), 9999)
    run_mode = os.environ.get('RUN_MODE', 'once') # defaults to 'once if RUN_MODE does not exist
    max_workers = int(os.environ.get('MAX_WORKERS', 1))

    if (run_mode == 'scheduled') and (speed in ['Standard', 'Fast', 'Rapid']):
        logger.info('Initializing run schedule')

        logger.info(f"Schedule configuration:")
        logger.info(f"  - Max workers: using {max_workers} workers")
        logger.info(f"  - Scraper type: {speed}")
        logger.info(f"  - Scrape interval: every {minute_interval} minutes")

        # Set the schedule - availability: 
        schedule.every(minute_interval).minutes.do(run_avail, speed=speed, max_workers=max_workers)

        logger.info("Schedule initialized. Starting scheduled execution loop")

        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every x seconds
    
    elif (run_mode == 'scheduled') and (speed == 'Locations'):
        logger.info('Initializing run schedule')

        logger.info(f"Schedule configuration:")
        logger.info(f"  - Scraper type: Locations")
        logger.info(f"  - Scrape interval: Every {location_day_interval} days")
        
        schedule.every(location_day_interval).days.do(run_locations)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every x seconds

    elif (run_mode == 'once') and (speed == 'Locations'):
        logger.info('Ran locations scraper.')
    
    elif (run_mode == 'once') and (speed in ['Standard', 'Fast', 'Rapid']):
        logger.info('Initializing run schedule')
        logger.info(f"  - Max workers: using {max_workers} workers")
        logger.info(f"Schedule configuration:")
        logger.info(f"  - Scraper type: {speed}")
        logger.info(f"  - Scrape interval: Once")

        run_avail(speed=speed, max_workers=max_workers)
    else:
        logger.warning(f"Scraper configs could not be resolved.")
