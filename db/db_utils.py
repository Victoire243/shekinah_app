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

    def insert_fields(self, table_name, fields, values):
        fields_str = ", ".join(fields)
        values_str = ", ".join([f"'{v}'" for v in values])
        self.cursor.execute(
            f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str})"
        )
        self.conn.commit()

    def add_medoc(self, medoc):
        self.insert_fields(
            "accounts_produit",
            [
                "nom",
                "marque",
                "date_entree",
                "date_dexpiration",
                "prix_achat",
                "prix_vente",
            ],
            medoc,
        )

    def delete_medoc(self, name):
        self.cursor.execute(f"DELETE FROM accounts_produit WHERE nom = '{name}'")
        self.conn.commit()

    def get_all_medocs_names(self):
        return self.cursor.execute("SELECT nom FROM accounts_produit").fetchall()

    def get_all_medocs_names_as_list(self):
        return [medoc[0] for medoc in self.get_all_medocs_names()]

    def get_medoc_quantity(self, name):
        return self.cursor.execute(
            f"SELECT quantite FROM accounts_produit WHERE nom = '{name}'"
        ).fetchone()[0]

    def update_medoc_quantity(self, name, quantity):
        self.cursor.execute(
            f"UPDATE accounts_produit SET quantite = '{quantity}' WHERE nom = '{name}'"
        )
        self.conn.commit()

    def update_medoc(self, name, fields, values):
        fields_str = ", ".join(
            [f"{field} = '{value}'" for field, value in zip(fields, values)]
        )
        self.cursor.execute(
            f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{name}'"
        )
        self.conn.commit()

    def get_medoc(self, name):
        return self.cursor.execute(
            f"SELECT * FROM accounts_produit WHERE nom = '{name}'"
        ).fetchone()

    def get_medoc_fields(self):
        return [
            description[0]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        ]

    def get_medoc_fields_types(self):
        return [
            description[2]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        ]

    def get_medoc_fields_as_dict(self):
        return {
            description[1]: description[2]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        }

    def get_medoc_fields_types_as_dict(self):
        return {
            description[1]: description[2]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        }

    def get_medoc_fields_as_list(self):
        return [
            description[1]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        ]

    def get_medoc_fields_types_as_list(self):
        return [
            description[2]
            for description in self.cursor.execute(
                "PRAGMA table_info(accounts_produit)"
            ).fetchall()
        ]


if __name__ == "__main__":
    db = DBUtils()
    print(db.get_medocs_for_list_preview())
    db.close()
