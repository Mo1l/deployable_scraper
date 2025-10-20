from db_tools import db
import json
import os
class test_db(db): 
    """
    test_db inherits from db. But adds some functions to shorten the test scripts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert_location_test_data(self):
        with open('tests/location_test.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)

        for k in locations['locations'].keys():
            v = locations['locations'][k]

            self.insert_row_in_locations_table(v)
        

    def clean_up_db(self):
        db_file = f'{self.name}.db'

        if os.path.exists(db_file):
            os.remove(db_file)
            

