
from test_tools import test_db as db
import sqlite3

test_db=db(name='test')

test_db.create_db()

test_db.insert_location_test_data()
test_db.insert_connectorGroup_test_data()

# ['Standard', 'Fast', 'Rapid', 'Unknown']
slocids=test_db.select_locationIds_by_speed('Standard')
flocids=test_db.select_locationIds_by_speed('Fast')
rlocids=test_db.select_locationIds_by_speed('Rapid')
ulocids=test_db.select_locationIds_by_speed('Unknown')

scount=len(slocids)
fcount=len(flocids)
rcount=len(rlocids)
ucount=len(ulocids)

tcount=scount + fcount + rcount + ucount 

conn = sqlite3.connect(f'{test_db.name}.db')
cursor = conn.cursor()    
cursor.execute(f"SELECT COUNT(*) FROM latest_connector_groups")
ncount = cursor.fetchone()[0]
assert tcount  ==  ncount, f'number of unique (location, connectorGroup) pairs should be 3145, but found {tcount}'

# clean up: 
conn.close()
test_db.clean_up_db()
