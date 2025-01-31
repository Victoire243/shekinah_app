import sqlite3
import datetime
import csv


class DBUtils:
    def __init__(self, db_path: str = "database/db.sqlite3"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def insert(self, table_name, values):
        values_str = ", ".join([f"'{v}'" for v in values])
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({values_str})")
        self.conn.commit()

    def select(self, table_name, columns):
        columns_str = ", ".join(columns)
        resultat = self.cursor.execute(
            f"SELECT {columns_str} FROM {table_name}"
        ).fetchall()
        return resultat if resultat else []

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
                "marque",
                "date_entree",
                "date_dexpiration",
                "prix_achat",
                "prix_vente",
            ],
        )

    def get_medocs_for_list_preview_by_containing_name(self, name: str):
        return self.cursor.execute(
            f"SELECT nom, marque, date_entree, date_dexpiration, prix_achat, prix_vente FROM accounts_produit WHERE nom LIKE '%{name.upper().strip()}%'"
        ).fetchall()

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

    def delete_medoc(self, name: str):
        self.cursor.execute(
            f"DELETE FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
        )
        self.conn.commit()

    def get_all_medocs_names(self):
        return self.cursor.execute("SELECT nom FROM accounts_produit").fetchall()

    def get_all_medocs_names_as_list(self):
        return [medoc[0] for medoc in self.get_all_medocs_names()]

    def get_medoc_quantity(self, name: str):
        return self.cursor.execute(
            f"SELECT quantite FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
        ).fetchone()[0]

    def get_medoc_quantity_by_id(self, id: int | str):
        result = self.cursor.execute(
            f"SELECT qte FROM accounts_mouvement WHERE produit_id = {id}"
        ).fetchone()
        return result[0] if result else 0

    def get_medoc_id_by_name(self, name: str):
        return self.cursor.execute(
            f"SELECT id FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
        ).fetchone()[0]

    def update_medoc_quantity_by_id(self, id: int | str, new_quantity: int | str):
        self.cursor.execute(
            f"UPDATE accounts_mouvement SET qte = {new_quantity} WHERE produit_id = {id}"
        )
        self.conn.commit()

    def update_medoc_designation_by_id(self, id: int | str, new_description: str):
        self.cursor.execute(
            f"UPDATE accounts_mouvement SET designation = '{new_description}' WHERE produit_id = {id}"
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

    def update_medoc_to_accounts_produit_by_medoc_name(
        self, medoc_name: str, fields, values
    ):
        fields_str = ", ".join(
            [f"{field} = '{value}'" for field, value in zip(fields, values)]
        )
        self.cursor.execute(
            f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{medoc_name}'"
        )
        self.conn.commit()

    def add_new_medoc_to_accounts_mouvement_out(
        self, designation, qte, pu, produit_id, pv
    ):
        medoc = (
            designation,
            qte,
            pu,
            "sortie",
            produit_id,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pv,
        )
        self.insert_fields(
            "accounts_mouvement",
            ("designation", "qte", "pu", "typ", "produit_id", "date", "pv"),
            medoc,
        )

    def add_to_accounts_mouvement_facture(
        self,
        quantite,
        forme,
        produit,
        prix_unitaire,
        prix_total,
        id_facture,
        nom_client,
        date,
    ):
        self.insert_fields(
            "accounts_mouvement_facture",
            (
                "quantité",
                "forme",
                "produit",
                "prix_unitaire",
                "prix_total",
                "id_facture",
                "nom_client",
                "date",
            ),
            (
                quantite,
                forme,
                produit,
                prix_unitaire,
                prix_total,
                id_facture,
                nom_client,
                date,
            ),
        )

    def get_all_mouvement_facture(self):
        return self.select("accounts_mouvement_facture", ["*"])

    def get_all_mouvement_facture_by_id_facture(self, id_facture):
        resultat = self.cursor.execute(
            f"SELECT * FROM accounts_mouvement_facture WHERE id_facture = {id_facture if id_facture else 0}"
        ).fetchall()
        return resultat if resultat else []

    def get_last_facture_id(self):
        result = self.cursor.execute(
            "SELECT id_facture FROM accounts_mouvement_facture facture ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else 0

    def get_last_mouve_id(self):
        result = self.cursor.execute(
            "SELECT id FROM accounts_mouvement ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else 0

    def import_csv_to_db(self, csv_file_path):
        try:
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.add_medoc(
                        (
                            row["nom"],
                            row["marque"],
                            row["date_entree"],
                            row["date_dexpiration"],
                            row["prix_achat"],
                            row["prix_vente"],
                        )
                    )
                    # Insert into accounts_mouvement
            print("CSV data has been imported into the database.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
