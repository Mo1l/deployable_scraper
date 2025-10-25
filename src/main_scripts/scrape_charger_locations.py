from scrapers.with_requests.scrape_locations_with_api import scraper 
from db_tools import db
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


