from test_tools import test_db as db
import sqlite3 

def test_insert_connectorGroups():
    try:
        test_db=db(name='test')
        test_db.create_db()
        test_db.insert_location_test_data()
        test_db.insert_connectorGroup_test_data()

        conn = sqlite3.connect(f'{test_db.name}.db')
        cursor = conn.cursor()    
        cursor.execute(f"SELECT COUNT(*) FROM ConnectorGroups")
        count = cursor.fetchone()[0]
        assert count == 3145, f'Inserted rows do not match, entries in JSON test file. is {count} but should be 3145'

    # clean up: 
    finally:
        conn.close()
        test_db.clean_up_db()

if __name__ == '__main__':
    test_insert_connectorGroups()

