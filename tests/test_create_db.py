from test_tools import test_db as db

def test_create_db():
    test_db = db(name='test')

    if test_db.check_if_db_exists():
        #print(f'To run this test first delete the {test_db.name}.db in the root directory')
        raise FileExistsError(f'To run this test first delete the {test_db.name}.db in the root directory')

    test_db.create_db()
    try:
        assert test_db.check_if_db_exists(), f'{test_db.name}.db was not created'
    finally:
        test_db.clean_up_db()

if __name__ == '__main__':
    test_create_db()