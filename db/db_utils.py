import sqlite3


class DBUtils:
    def __init__(self, db_path: str = "db.sqlite3"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name, columns):
        columns_str = ", ".join(columns)
        self.cursor.execute(f"CREATE TABLE {table_name} ({columns_str})")
        self.conn.commit()

    def insert(self, table_name, values):
        values_str = ", ".join([f"'{v}'" for v in values])
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({values_str})")
        self.conn.commit()

    def select(self, table_name, columns):
        columns_str = ", ".join(columns)
        return self.cursor.execute(f"SELECT {columns_str} FROM {table_name}").fetchall()

    def close(self):
        self.conn.close()

    def get_all_medocs_list(self):
        medocs = self.select("accounts_produit", ["nom"])
        medocs = (medoc[0] for medoc in medocs)
        return list(medocs)

    def list_tables(self):
        return self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

    def get_all_medocs(self):
        return self.select("accounts_produit", ["*"])

    def get_medocs_for_list_preview(self):
        return self.select(
            "accounts_produit",
            [
                "nom",
                "designation_entree",
                "date_entree",
                "date_dexpiration",
                "prix_achat",
                "prix_vente",
            ],
        )

    async def get_medocs_by_name(self, name: str):
        return self.cursor.execute(
            f"SELECT * FROM accounts_produit WHERE nom = '{name.upper()}'"
        ).fetchall()

    def is_medoc_exists(self, name: str):
        return bool(
            self.cursor.execute(
                f"SELECT * FROM accounts_produit WHERE nom = '{name.upper()}'"
            ).fetchall()
        )


if __name__ == "__main__":
    db = DBUtils()
    print(db.get_medocs_for_list_preview())
    db.close()
