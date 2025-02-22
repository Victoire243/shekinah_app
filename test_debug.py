# Description: Debugging test file for the db_utils.py file
from db.db_utils import DBUtils

db = DBUtils("assets/db/db_test.sqlite3")

print(db.get_all_medocs_names_quantity_expiration_date())
