from test_tools import test_db as db
import json 
import numpy as np
import sqlite3 
test_db=db(name='test')

test_db.create_db()

test_db.insert_location_test_data()

conn = sqlite3.connect(test_db.name + '.db')
cursor = conn.cursor()    
cursor.execute(f"SELECT COUNT(*) FROM locations")
count = cursor.fetchone()[0]
assert count == 2960, f'Inserted rows do not match, entries in JSON test file. is {count} but should be 2960'

# clean up: 
test_db.clean_up_db()
