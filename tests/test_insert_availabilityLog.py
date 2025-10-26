from test_tools import test_db as db
import json
import sqlite3 

def test_insert_availabilityLog():
    try:
        # creating test environment.
        test_db=db(name='test')
        test_db.create_db()
        test_db.insert_location_test_data()

        with open('tests/availability_test.json', 'r', encoding='utf-8') as f:
            availability = json.load(f)

        for k in availability.keys():
            v = availability[k]
            test_db.insert_row_in_availabilityLog_table(loc_avail_query=v)

        conn = sqlite3.connect(f'{test_db.name}.db')
        cursor = conn.cursor()    
        cursor.execute(f"SELECT COUNT(*) FROM availabilityLog")
        count_availabilityLog = cursor.fetchone()[0]
        assert count_availabilityLog == 30, f'there should be 30 entries, but db have {count_availabilityLog}'

        cursor.execute(f"SELECT COUNT(*) FROM evseIds")
        count_evseIds = cursor.fetchone()[0]
        assert count_evseIds == 30, f'there should be 30 entries, but db have {count_evseIds}'

    finally:
        conn.close()
        # clean up: 
        test_db.clean_up_db()

if __name__ == '__main__':
    test_insert_availabilityLog()
