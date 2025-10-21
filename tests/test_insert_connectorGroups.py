from test_tools import test_db as db
import sqlite3 

test_db=db(name='test')
test_db.create_db()
test_db.insert_location_test_data()
test_db.insert_connectorGroup_test_data()


conn = sqlite3.connect(test_db.name + '.db')
cursor = conn.cursor()    
cursor.execute(f"SELECT COUNT(*) FROM ConnectorGroups")
count = cursor.fetchone()[0]
breakpoint()
assert count == 3145, f'Inserted rows do not match, entries in JSON test file. is {count} but should be 3145'

# clean up: 
conn.close()
breakpoint()
test_db.clean_up_db()
