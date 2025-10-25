from scrapers.with_requests.scrape_availability_with_api import scraper 
from db_tools import db
import schedule
import os
import time
from datetime import datetime 

def run(speed): 
    # options: 
    speed = 'Fast'

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

if __name__ == "__main__":
    run_mode = os.environ.get('RUN_MODE', 'once') # defaults to 'once if RUN_MODE does not exist

    if run_mode == 'scheduled':
        # Schedule at quarter hours: :00, :15, :30, :45
        schedule.every().hour.at(":00").do(run_scraper)  # Top of hour
        schedule.every().hour.at(":15").do(run_scraper)  # First quarter
        schedule.every().hour.at(":30").do(run_scraper)  # Second quarter  
        schedule.every().hour.at(":45").do(run_scraper)  # Third quarter
        
        print("Scheduled to run every 15 minutes at :00, :15, :30, :45")
        print("Next runs will be at the quarter hours")
        
        # Keep running scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every x seconds
            
    else:
        # Run once and exit (default behavior)
        run()