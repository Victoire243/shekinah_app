import sqlite3


class DBUtils:
    def __init__(self, db_path: str = "database/db.sqlite3"):
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

    def get_medocs_by_name(self, name: str):
        return self.cursor.execute(
            f"SELECT * FROM accounts_produit WHERE nom = '{name.upper()}'"
        ).fetchall()

    def is_medoc_exists(self, name: str):
        return bool(
            self.cursor.execute(
                f"SELECT * FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            ).fetchall()
        )

    def insert_fields(self, table_name, fields: tuple, values: tuple):
        all_fields = self.get_table_fields_as_list(table_name)
        fields_str = ", ".join(fields)
        values_str = ", ".join([f"'{v}'" for v in values])

        # Add default value based on field type for missing fields, excluding 'id'
        field_types = self.get_table_fields_types_as_dict(table_name)
        for field in all_fields:
            if field not in fields and field != "id":
                fields_str += f", {field}"
                field_type = field_types.get(field, "TEXT")
                if field_type == "INTEGER":
                    values_str += ", 0"
                elif field_type == "REAL":
                    values_str += ", 0.0"
                else:
                    values_str += ", 'non classé'"

        self.cursor.execute(
            f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str})"
        )
        self.conn.commit()

    def add_medoc(self, medoc: list | tuple):
        self.insert_fields(
            "accounts_produit",
            (
                "nom",
                "marque",
                "date_entree",
                "date_dexpiration",
                "prix_achat",
                "prix_vente",
            ),
            medoc,
        )
        self.add_new_medoc_to_accounts_mouvement(medoc)

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

    def get_table_fields_as_list(self, table_name="accounts_produit"):
        return [
            description[1]
            for description in self.cursor.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        ]

    def get_table_fields_types_as_dict(self, table_name):
        return {
            description[1]: description[2]
            for description in self.cursor.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        }

    def update_medoc_fields(self, name, fields, values):
        fields_str = ", ".join(
            [f"{field} = '{value}'" for field, value in zip(fields, values)]
        )
        self.cursor.execute(
            f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{name}'"
        )
        self.conn.commit()

    def add_new_medoc_to_accounts_mouvement(self, medoc):
        medoc = (
            medoc[2],
            medoc[1],
            0,
            medoc[4],
            "entrée",
            self.cursor.execute(
                f"SELECT id FROM accounts_produit WHERE nom = '{medoc[0]}'"
            ).fetchone()[0],
            medoc[5],
        )
        self.insert_fields(
            "accounts_mouvement",
            ("date", "designation", "qte", "pu", "typ", "produit_id", "pv"),
            medoc,
        )


if __name__ == "__main__":
    db = DBUtils()
    db.add_medoc(
        [
            "DOPRO",
            "SANOFI",
            "2021-09-01",
            "2023-09-01",
            5,
            10,
        ]
    )
    db.close()
