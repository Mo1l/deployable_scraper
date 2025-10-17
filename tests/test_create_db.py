from db_tools import db


test_db = db(name='test')

if test_db.check_if_db_exists():
    #print(f'To run this test first delete the {test_db.name}.db in the root directory')
    raise FileExistsError(f'To run this test first delete the {test_db.name}.db in the root directory')

test_db.create_db()

assert test_db.check_if_db_exists(), f'{test_db.name}.db was not created'
