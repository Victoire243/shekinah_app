import sqlite3
from db.db_utils import DBUtils

db = DBUtils("assets/db/db_test.sqlite3")

print(db.get_all_mouvement_facture_by_client_name("E"))