from scrapers.with_requests.scrape_availability_with_api import scraper 
from db_tools import db

# options: 
speed = 'Rapid'

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
availability_scraper.run(max_workers=4)
availability = availability_scraper.results

for locationId in availability.keys():
    v = availability[locationId]['data']
    database.insert_row_in_availabilityLog_table(loc_avail_query=v)



