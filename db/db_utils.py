import sqlite3
import datetime
import csv


class DBUtils:
    def __init__(self, db_path: str = "database/db.sqlite3"):
        try:
            self.db_path = db_path
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        except sqlite3.Error as e:
            print(f"An error occurred while connecting to the database: {e}")

    def insert(self, table_name, values):
        cursor = None
        try:
            cursor = self.conn.cursor()
            all_fields = self.get_table_fields_as_list(table_name)
            field_types = self.get_table_fields_types_as_dict(table_name)
            values_str = ", ".join([f"'{v}'" for v in values])

            # Ajoute une valeur par défaut en fonction du type pour les champs manquants, sauf 'id'
            for field in all_fields[len(values) :]:
                if field != "id":
                    field_type = field_types.get(field, "TEXT")
                    if field_type.upper() == "INTEGER":
                        values_str += ", 0"
                    elif field_type.upper() == "REAL":
                        values_str += ", 0.0"
                    else:
                        values_str += ", 'non classé'"

            cursor.execute(f"INSERT INTO {table_name} VALUES ({values_str})")
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting data: {e}")
        finally:
            if cursor:
                cursor.close()

    def select(self, table_name, columns):
        cursor = None
        try:
            cursor = self.conn.cursor()
            columns_str = ", ".join(columns)
            resultat = cursor.execute(
                f"SELECT {columns_str} FROM {table_name}"
            ).fetchall()
            return resultat if resultat else []
        except sqlite3.Error as e:
            print(f"An error occurred while selecting data: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"An error occurred while closing the database connection: {e}")

    def get_all_medocs_list(self):
        try:
            medocs = self.select("accounts_produit", ["nom"])
            medocs = (medoc[0] for medoc in medocs)
            return list(medocs)
        except Exception as e:
            print(f"An error occurred while getting all medocs list: {e}")
            return []

    def list_tables(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            result = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ).fetchall()
            return result
        except sqlite3.Error as e:
            print(f"An error occurred while listing tables: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_medocs(self):
        try:
            return self.select("accounts_produit", ["*"])
        except Exception as e:
            print(f"An error occurred while getting all medocs: {e}")
            return []

    def get_medocs_for_list_preview(self):
        try:
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
        except Exception as e:
            print(f"An error occurred while getting medocs for list preview: {e}")
            return []

    def get_medocs_for_list_preview_by_containing_name(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                "SELECT nom, marque, date_entree, date_dexpiration, prix_achat, prix_vente "
                f"FROM accounts_produit WHERE nom LIKE '%{name.upper().strip()}%'"
            )
            result = cursor.execute(query).fetchall()
            return result if result else []
        except sqlite3.Error as e:
            print(f"An error occurred while getting medocs by containing name: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_medocs_by_name(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT * FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            )
            resultat = cursor.execute(query).fetchall()
            return resultat if resultat else []
        except sqlite3.Error as e:
            print(f"An error occurred while getting medocs by name: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def is_medoc_exists(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT 1 FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            )
            result = cursor.execute(query).fetchone()
            return result is not None
        except sqlite3.Error as e:
            print(f"An error occurred while checking if medoc exists: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def insert_fields(self, table_name, fields: tuple, values: tuple):
        cursor = None
        try:
            all_fields = self.get_table_fields_as_list(table_name)
            fields_str = ", ".join(fields)
            values_str = ", ".join([f"'{v}'" for v in values])

            # Ajoute une valeur par défaut en fonction du type pour les champs manquants, sauf 'id'
            field_types = self.get_table_fields_types_as_dict(table_name)
            for field in all_fields:
                if field not in fields and field != "id":
                    fields_str += f", {field}"
                    field_type = field_types.get(field, "TEXT")
                    if field_type.upper() == "INTEGER":
                        values_str += ", 0"
                    elif field_type.upper() == "REAL":
                        values_str += ", 0.0"
                    else:
                        values_str += ", 'non classé'"

            cursor = self.conn.cursor()
            query = f"INSERT INTO {table_name} ({fields_str}) VALUES ({values_str})"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting fields: {e}")
        finally:
            if cursor:
                cursor.close()

    def add_medoc(self, medoc: list | tuple):
        try:
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
        except Exception as e:
            print(f"An error occurred while adding medoc: {e}")

    def delete_medoc(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"DELETE FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting medoc: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_all_medocs_names(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            result = cursor.execute("SELECT nom FROM accounts_produit").fetchall()
            return result
        except sqlite3.Error as e:
            print(f"An error occurred while getting all medocs names: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_medocs_names_as_list(self):
        try:
            return [medoc[0] for medoc in self.get_all_medocs_names()]
        except Exception as e:
            print(f"An error occurred while getting all medocs names as list: {e}")
            return []

    def get_medoc_quantity(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"SELECT quantite FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            result = cursor.execute(query).fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc quantity: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_medoc_quantity_by_id(self, id: int | str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"SELECT qte FROM accounts_mouvement WHERE produit_id = {id}"
            result = cursor.execute(query).fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc quantity by id: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_medoc_id_by_name(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT id FROM accounts_produit WHERE nom = '{name.upper().strip()}'"
            )
            result = cursor.execute(query).fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc id by name: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def update_medoc_quantity_by_id(self, id: int | str, new_quantity: int | str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"UPDATE accounts_mouvement SET qte = {new_quantity} WHERE produit_id = {id}"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while updating medoc quantity by id: {e}")
        finally:
            if cursor:
                cursor.close()

    def update_medoc_designation_by_id(self, id: int | str, new_description: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"UPDATE accounts_mouvement SET designation = '{new_description}' "
                f"WHERE produit_id = {id}"
            )
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while updating medoc designation by id: {e}")
        finally:
            if cursor:
                cursor.close()

    def update_medoc(self, name, fields, values):
        cursor = None
        try:
            cursor = self.conn.cursor()
            fields_str = ", ".join(
                [f"{field} = '{value}'" for field, value in zip(fields, values)]
            )
            query = f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{name}'"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while updating medoc: {e}")
        finally:
            if cursor:
                cursor.close()

    def get_medoc(self, name):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"SELECT * FROM accounts_produit WHERE nom = '{name}'"
            result = cursor.execute(query).fetchone()
            return result
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc: {e}")
            return None
        finally:
            if cursor:
                cursor.close()

    def get_medoc_fields(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "PRAGMA table_info(accounts_produit)"
            result = cursor.execute(query).fetchall()
            return [description[0] for description in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc fields: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_medoc_fields_types(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "PRAGMA table_info(accounts_produit)"
            result = cursor.execute(query).fetchall()
            return [description[2] for description in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc fields types: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_medoc_fields_as_dict(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "PRAGMA table_info(accounts_produit)"
            result = cursor.execute(query).fetchall()
            return {description[1]: description[2] for description in result}
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc fields as dict: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def get_medoc_fields_types_as_dict(self):
        # Même implémentation que get_medoc_fields_as_dict()
        return self.get_medoc_fields_as_dict()

    def get_medoc_fields_as_list(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "PRAGMA table_info(accounts_produit)"
            result = cursor.execute(query).fetchall()
            return [description[1] for description in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc fields as list: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_medoc_fields_types_as_list(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "PRAGMA table_info(accounts_produit)"
            result = cursor.execute(query).fetchall()
            return [description[2] for description in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc fields types as list: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_table_fields_as_list(self, table_name="accounts_produit"):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"PRAGMA table_info({table_name})"
            result = cursor.execute(query).fetchall()
            return [description[1] for description in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting table fields as list: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_table_fields_types_as_dict(self, table_name):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"PRAGMA table_info({table_name})"
            result = cursor.execute(query).fetchall()
            return {description[1]: description[2] for description in result}
        except sqlite3.Error as e:
            print(f"An error occurred while getting table fields types as dict: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()

    def update_medoc_fields(self, name, fields, values):
        cursor = None
        try:
            cursor = self.conn.cursor()
            fields_str = ", ".join(
                [f"{field} = '{value}'" for field, value in zip(fields, values)]
            )
            query = f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{name}'"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while updating medoc fields: {e}")
        finally:
            if cursor:
                cursor.close()

    def add_new_medoc_to_accounts_mouvement(self, medoc):
        cursor = None
        try:
            cursor = self.conn.cursor()
            # Récupère l'ID du medoc inséré
            query = f"SELECT id FROM accounts_produit WHERE nom = '{medoc[0]}'"
            medoc_id = cursor.execute(query).fetchone()[0]
            # Construit le tuple pour accounts_mouvement
            mouvement = (
                medoc[2],  # date_entree
                medoc[1],  # marque ou designation (selon votre logique)
                100,  # quantité par défaut (à adapter si besoin)
                medoc[4],  # prix_achat
                "entrée",  # type de mouvement
                medoc_id,  # id du medoc
                medoc[5],  # prix_vente
            )
            # Insère dans accounts_mouvement via insert_fields
            self.insert_fields(
                "accounts_mouvement",
                ("date", "designation", "qte", "pu", "typ", "produit_id", "pv"),
                mouvement,
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(
                f"An error occurred while adding new medoc to accounts mouvement: {e}"
            )
        finally:
            if cursor:
                cursor.close()

    def update_medoc_to_accounts_produit_by_medoc_name(
        self, medoc_name: str, fields, values
    ):
        cursor = None
        try:
            cursor = self.conn.cursor()
            fields_str = ", ".join(
                [f"{field} = '{value}'" for field, value in zip(fields, values)]
            )
            query = (
                f"UPDATE accounts_produit SET {fields_str} WHERE nom = '{medoc_name}'"
            )
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(
                f"An error occurred while updating medoc to accounts produit by medoc name: {e}"
            )
        finally:
            if cursor:
                cursor.close()

    def add_new_medoc_to_accounts_mouvement_out(
        self, designation, qte, pu, produit_id, pv
    ):
        try:
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
        except sqlite3.Error as e:
            print(
                f"An error occurred while adding new medoc to accounts mouvement out: {e}"
            )

    def add_new_medoc_to_accounts_mouvement_in(
        self, designation, qte, pu, produit_id, pv
    ):
        try:
            medoc = (
                designation,
                qte,
                pu,
                "entree",
                produit_id,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                pv,
            )
            self.insert_fields(
                "accounts_mouvement",
                ("designation", "qte", "pu", "typ", "produit_id", "date", "pv"),
                medoc,
            )
        except sqlite3.Error as e:
            print(
                f"An error occurred while adding new medoc to accounts mouvement in: {e}"
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
        devise,
        reductions,
        charges_connexes,
    ):
        try:
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
                    "devise",
                    "reductions",
                    "charges_connexes",
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
                    devise,
                    reductions,
                    charges_connexes,
                ),
            )
        except sqlite3.Error as e:
            print(f"An error occurred while adding to accounts mouvement facture: {e}")

    def get_all_mouvement_facture(self):
        try:
            return self.select("accounts_mouvement_facture", ["*"])
        except Exception as e:
            print(f"An error occurred while getting all mouvement facture: {e}")
            return []

    def get_all_mouvement_facture_by_id_facture(self, id_facture):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT * FROM accounts_mouvement_facture WHERE id_facture = "
                f"{id_facture if id_facture else 0}"
            )
            resultat = cursor.execute(query).fetchall()
            return resultat if resultat else []
        except sqlite3.Error as e:
            print(
                f"An error occurred while getting all mouvement facture by id facture: {e}"
            )
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_mouvement_facture_by_client_name(self, client_name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT * FROM accounts_mouvement_facture WHERE nom_client LIKE "
                f"'%{client_name if client_name else ''}%'"
            )
            resultat = cursor.execute(query).fetchall()
            return resultat if resultat else []
        except sqlite3.Error as e:
            print(
                f"An error occurred while getting all mouvement facture by client name facture: {e}"
            )
            return []
        finally:
            if cursor:
                cursor.close()

    def get_last_facture_id(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT id_facture FROM accounts_mouvement_facture facture ORDER BY id DESC LIMIT 1"
            result = cursor.execute(query).fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting last facture id: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_last_mouve_id(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT id FROM accounts_mouvement ORDER BY id DESC LIMIT 1"
            result = cursor.execute(query).fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting last mouve id: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def import_csv_to_db(self, csv_file_path):
        try:
            with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.add_medoc(
                        (
                            row["nom"].upper().strip(),
                            row["designation_entree"].upper().strip(),
                            row["date_entree"],
                            row["date_dexpiration"],
                            row["prix_achat"],
                            row["prix_vente"],
                        )
                    )
            print("CSV data has been imported into the database.")
        except (sqlite3.Error, IOError) as e:
            print(f"An error occurred while importing CSV to DB: {e}")

    def delete_all_table_data(self, table_name):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = f"DELETE FROM {table_name}"
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while deleting all table data: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_all_data(self):
        try:
            tables = self.list_tables()
            for table in tables:
                self.delete_all_table_data(table[0])
        except Exception as e:
            print(f"An error occurred while deleting all data: {e}")

    def update_medocs_quantities(self, names: tuple | list, quantities: tuple | list):
        try:
            for name, quantity in zip(names, quantities):
                medoc_id = self.get_medoc_id_by_name(name)
                self.update_medoc_quantity_by_id(medoc_id, quantity)
        except Exception as e:
            print(f"An error occurred while updating medocs quantities: {e}")

    def get_medoc_quantity_by_name(self, name: str):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                f"SELECT qte FROM accounts_mouvement WHERE produit_id = "
                f"(SELECT id FROM accounts_produit WHERE nom = '{name.upper().strip()}')"
            )
            result = cursor.execute(query).fetchone()
            return result[0] if result and result[0] else 0
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc quantity by name: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_all_medocs_names_quantity_expiration_date(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                "SELECT accounts_produit.nom, accounts_mouvement.qte, "
                "accounts_produit.date_dexpiration FROM accounts_produit "
                "INNER JOIN accounts_mouvement ON accounts_produit.id = accounts_mouvement.produit_id"
            )
            result = cursor.execute(query).fetchall()
            return result
        except sqlite3.Error as e:
            print(
                f"An error occurred while getting all medocs names quantity expiration date: {e}"
            )
            return []
        finally:
            if cursor:
                cursor.close()

    def get_all_clients_names(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = "SELECT DISTINCT nom_client FROM accounts_mouvement_facture"
            result = cursor.execute(query).fetchall()
            return [client[0] for client in result]
        except sqlite3.Error as e:
            print(f"An error occurred while getting all clients names: {e}")
            return []
        finally:
            if cursor:
                cursor.close()

    def get_medoc_plus_vendu(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                "SELECT produit, SUM(quantité) FROM accounts_mouvement_facture "
                "GROUP BY produit ORDER BY SUM(quantité) DESC"
            )
            result = cursor.execute(query).fetchone()
            return result[0] if result else "Aucun médicament vendu"
        except sqlite3.Error as e:
            print(f"An error occurred while getting medoc plus vendu: {e}")
            return "Aucun médicament vendu"
        finally:
            if cursor:
                cursor.close()

    def get_top_client(self):
        cursor = None
        try:
            cursor = self.conn.cursor()
            query = (
                "SELECT nom_client, SUM(prix_total) FROM accounts_mouvement_facture "
                "GROUP BY nom_client ORDER BY SUM(prix_total) DESC"
            )
            result = cursor.execute(query).fetchone()
            return f"{result[0]} ({result[1]} FC)" if result else "Aucun client"
        except sqlite3.Error as e:
            print(f"An error occurred while getting top client: {e}")
            return "Aucun client"
        finally:
            if cursor:
                cursor.close()


if __name__ == "__main__":
    db = DBUtils("assets/db/db_test.sqlite3")
    # db.delete_all_table_data("accounts_mouvement_facture")
    # db.import_csv_to_db("assets/db/produits.csv")
    # db.delete_all_data()
    db.close()
