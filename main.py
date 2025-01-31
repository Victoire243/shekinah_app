import datetime
import flet as ft
from components.CustomElevatedButton import CustomElevatedButton
from components.CustomDraftButton import CustomDraftButton
from components.CustomTextField import CustomTextField
from utils.nombre_to_chiffre import number_to_words
from models.medicament_entree import MedicamentEntree
from utils.impression_facture import generer_facture
from views.login_view import LoginView
from models.medicament import Medicament
from pathlib import Path
from utils.speaker import Speaker
from flet import *
from db.db_utils import DBUtils
from threading import Thread

current_directory = (
    str(Path(__file__).parent.resolve()).replace("\\", "/")
    + "/assets/db/db_test.sqlite3"
)

db = DBUtils(current_directory)
list_medocs_names = db.get_all_medocs_list()
list_medocs_for_preview = db.get_medocs_for_list_preview()


def update_lists_medocs():
    global list_medocs_for_preview
    global list_medocs_names
    list_medocs_names = db.get_all_medocs_list()
    list_medocs_for_preview = db.get_medocs_for_list_preview()


class ProduitsView(Column):
    def __init__(
        self, page: ft.Page, handler_entree_produit=None, handler_entree_stock=None
    ):
        super().__init__()
        self.page = page
        self.handler_entree_produit = handler_entree_produit
        self.handler_entree_stock = handler_entree_stock
        self.current_page = 0
        self.items_per_page = 50
        self.total_items = len(list_medocs_for_preview)
        self.total_pages = (
            self.total_items + self.items_per_page - 1
        ) // self.items_per_page
        self.search_bar = SearchBar(
            bar_bgcolor="white",
            bar_elevation=1,
            bar_border_side=BorderSide(width=0),
            width=250,
            height=40,
            view_shape=RoundedRectangleBorder(10),
            bar_shape=RoundedRectangleBorder(10),
            bar_hint_text="Rechercher...",
            bar_leading=Icon(Icons.SEARCH, color="black"),
            bar_trailing=[
                IconButton(
                    Icons.CLOSE,
                    icon_color="black",
                    icon_size=18,
                    on_click=lambda e: self.page.run_task(self.__restore_search_bar),
                )
            ],
            on_blur=lambda e: self.page.run_task(self.__search_medoc),
        )
        self.data_table = DataTable(
            sort_column_index=0,
            heading_row_color={ControlState.DEFAULT: "blue"},
            sort_ascending=True,
            data_row_color={ControlState.HOVERED: "blue"},
            columns=[
                DataColumn(
                    label=Text(
                        "Désignation",
                        weight=FontWeight.BOLD,
                        color="white",
                    ),
                ),
                DataColumn(label=Text("Forme", weight=FontWeight.BOLD, color="white")),
                DataColumn(
                    label=Text(
                        "Date d'entrée",
                        weight=FontWeight.BOLD,
                        color="white",
                    )
                ),
                DataColumn(
                    label=Text(
                        "Date d'expiration",
                        weight=FontWeight.BOLD,
                        color="white",
                    )
                ),
                DataColumn(
                    label=Text(
                        "Prix d'achat",
                        weight=FontWeight.BOLD,
                        color="white",
                    ),
                    numeric=True,
                ),
                DataColumn(
                    label=Text(
                        "Prix de vente",
                        weight=FontWeight.BOLD,
                        color="white",
                    ),
                    numeric=True,
                ),
                DataColumn(
                    label=Text("Stock", weight=FontWeight.BOLD, color="white"),
                    numeric=True,
                ),
                DataColumn(
                    label=Text("Actions", weight=FontWeight.BOLD, color="white")
                ),
            ],
            rows=list(self.__products()),
        )
        self.controls = [
            Container(
                bgcolor="black",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Row(
                    controls=[
                        Text(
                            "Liste des produits",
                            color="white",
                            weight=FontWeight.BOLD,
                            size=20,
                        ),
                        Row(
                            controls=[
                                self.search_bar,
                                Button(
                                    "+ Produit",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="blue",
                                    ),
                                    on_click=self.handler_entree_produit,
                                ),
                                Button(
                                    "+ Entrée Stock",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="blue",
                                    ),
                                    on_click=self.handler_entree_stock,
                                ),
                                Button(
                                    " ",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="white",
                                    ),
                                    icon=Icons.LOOP,
                                    icon_color="blue",
                                ),
                            ],
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            Container(
                expand=True,
                padding=padding.symmetric(horizontal=10, vertical=10),
                content=Column(
                    scroll=ScrollMode.AUTO,
                    controls=[self.data_table],
                ),
            ),
            Row(
                alignment=MainAxisAlignment.CENTER,
                controls=[
                    Button(
                        "Page Précédente",
                        on_click=self.__previous_page,
                        disabled=self.current_page == 0,
                        elevation=1,
                        style=ButtonStyle(
                            shape=RoundedRectangleBorder(10),
                            color="white",
                            bgcolor="blue",
                        ),
                    ),
                    Text(f"Page {self.current_page + 1} sur {self.total_pages}"),
                    Button(
                        "Page Suivante",
                        on_click=self.__next_page,
                        disabled=self.current_page >= self.total_pages - 1,
                        elevation=1,
                        style=ButtonStyle(
                            shape=RoundedRectangleBorder(10),
                            color="white",
                            bgcolor="blue",
                        ),
                    ),
                ],
            ),
        ]

    async def __restore_search_bar(self):
        self.search_bar.value = ""
        self.search_bar.update()
        self.data_table.rows = list(self.__products())
        await self.data_table.update_async()

    async def __search_medoc(self):
        products_founds = db.get_medocs_for_list_preview_by_containing_name(
            self.search_bar.value
        )
        if products_founds:
            self.data_table.rows = list(self.__products_searched(products_founds))
            await self.data_table.update_async()
        else:
            self.page.snack_bar = SnackBar(Text("Aucun produit trouvé"), open=True)
        await self.page.update_async()

    def __products_searched(self, products_founds):
        for medoc in products_founds:
            try:
                quantite = db.get_medoc_quantity_by_id(
                    db.get_medoc_id_by_name(medoc[0])
                )
            except:
                quantite = 0
            yield DataRow(
                cells=[
                    DataCell(Text(medoc[0])),
                    DataCell(Text(medoc[1])),
                    DataCell(Text(medoc[2])),
                    DataCell(Text(medoc[3])),
                    DataCell(Text(medoc[4])),
                    DataCell(Text(medoc[5])),
                    DataCell(Text(str(quantite))),
                    DataCell(
                        IconButton(
                            Icons.EDIT,
                            icon_color="blue",
                            on_click=self.__handler_edit_button,
                        )
                    ),
                ]
            )

    def __products(self):
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        for medoc in list_medocs_for_preview[start_index:end_index]:
            try:
                quantite = db.get_medoc_quantity_by_id(
                    db.get_medoc_id_by_name(medoc[0])
                )
            except:
                quantite = 0
            yield DataRow(
                cells=[
                    DataCell(Text(medoc[0])),
                    DataCell(Text(medoc[1])),
                    DataCell(Text(medoc[2])),
                    DataCell(Text(medoc[3])),
                    DataCell(Text(medoc[4])),
                    DataCell(Text(medoc[5])),
                    DataCell(Text(str(quantite))),
                    DataCell(
                        IconButton(
                            Icons.EDIT,
                            icon_color="blue",
                            on_click=self.__handler_edit_button,
                        )
                    ),
                ]
            )

    def __next_page(self, e):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.__update_table()

    def __previous_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
            self.__update_table()

    def __update_table(self):
        self.data_table.rows = list(self.__products())
        self.controls[-1].controls[
            1
        ].value = f"Page {self.current_page + 1} sur {self.total_pages}"
        self.controls[-1].controls[0].disabled = self.current_page == 0
        self.controls[-1].controls[2].disabled = (
            self.current_page >= self.total_pages - 1
        )
        self.data_table.update()
        self.page.update()

    def __handler_edit_button(self, e: ControlEvent):
        m = []
        for medoc in e.control.parent.parent.cells[:-1]:
            m.append(medoc.content.value)
        self.__modifie_medoc(m)

    def __modifie_medoc(self, medoc: list | list):
        self.ancien_nom = medoc[0].strip().upper() if medoc[0] else " "
        self.nom = CustomTextField(
            label="Nom du produit",
            height=60,
            value=medoc[0],
        )
        self.forme = CustomTextField(
            label="Forme du produit", height=60, value=medoc[1]
        )
        self.prix_achat = CustomTextField(
            label="Prix d'achat",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            value=medoc[4],
            height=60,
        )
        self.prix_vente = CustomTextField(
            label="Prix de vente",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            value=medoc[5],
            height=60,
        )
        self.current_date = datetime.datetime.now()
        self.stock_quantite = CustomTextField(
            label="Stock",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            value=medoc[6],
            height=60,
        )
        self.date_field = CustomTextField(
            label="Date d'expiration",
            read_only=True,
            height=60,
            value=str(medoc[3]),
            prefix_icon=Icon(Icons.CALENDAR_TODAY, color="black"),
            on_click=lambda e: self.page.open(
                DatePicker(
                    first_date=datetime.datetime(year=2010, month=1, day=1),
                    last_date=datetime.datetime(year=2050, month=1, day=1),
                    current_date=self.current_date,
                    cancel_text="Annuler",
                    on_change=self.__select_date,
                )
            ),
        )
        self.button_mettre_a_jour = Button(
            "Mettre à jour",
            elevation=1,
            style=ButtonStyle(
                shape=RoundedRectangleBorder(10),
                color="white",
                bgcolor="blue",
            ),
            width=200,
            on_click=lambda e: self.page.run_thread(
                self.__update_medoc_accounts_produit_db
            ),
        )
        self.dialog = AlertDialog(
            scrollable=True,
            adaptive=True,
            title=Text("Modifier un produit"),
            bgcolor="#f0f0f0",
            content=Column(
                expand=True,
                controls=[
                    self.nom,
                    self.forme,
                    self.prix_achat,
                    self.prix_vente,
                    self.date_field,
                    self.stock_quantite,
                ],
            ),
            actions=[
                Button(
                    "Supprimer",
                    elevation=1,
                    style=ButtonStyle(
                        shape=RoundedRectangleBorder(10),
                        color="white",
                        bgcolor="red",
                    ),
                    width=200,
                    on_click=lambda e: self.page.run_thread(
                        self.__delete_medoc_accounts_produit_db
                    ),
                ),
                self.button_mettre_a_jour,
            ],
        )

        self.page.open(self.dialog)
        self.page.update()

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        self.date_field.update()

    def __update_medoc_accounts_produit_db(self):
        self.page.run_task(self.__update_medoc_accounts_produit_db_async)

    async def __update_medoc_accounts_produit_db_async(self):
        if (
            self.nom.value
            and self.prix_achat.value
            and self.prix_vente.value
            and self.forme.value
        ):
            try:
                db.update_medoc_to_accounts_produit_by_medoc_name(
                    medoc_name=self.ancien_nom,
                    fields=(
                        "nom",
                        "marque",
                        "prix_achat",
                        "prix_vente",
                        "date_dexpiration",
                    ),
                    values=(
                        self.nom.value.upper().strip(),
                        self.forme.value.upper().strip(),
                        self.prix_achat.value,
                        self.prix_vente.value,
                        self.date_field.value,
                    ),
                )
                medoc_id = db.get_medoc_id_by_name(self.nom.value)
                db.update_medoc_quantity_by_id(medoc_id, int(self.stock_quantite.value))
                db.update_medoc_designation_by_id(medoc_id, self.forme.value)
            except:
                self.page.snack_bar = SnackBar(
                    Text("Une erreur est survenue, veuillez ressayer !"), open=True
                )
            else:
                update_lists_medocs()
                self.page.close(self.dialog)
                self.page.snack_bar = SnackBar(
                    Text("Le produit a été modifié avec succès"), open=True
                )
                self.data_table.rows = list(self.__products())
                await self.data_table.update_async()
            finally:
                await self.page.update_async()

    def __delete_medoc_accounts_produit_db(self):
        self.page.run_task(self.__delete_medoc_accounts_produit_db_async)

    async def __delete_medoc_accounts_produit_db_async(self):
        if self.nom.value:
            try:
                db.delete_medoc(self.nom.value)
            except:
                self.page.snack_bar = SnackBar(
                    Text("Une erreur est survenue, veuillez ressayer !"), open=True
                )
            else:
                update_lists_medocs()
                self.page.close(self.dialog)
                self.page.snack_bar = SnackBar(
                    Text("Le produit a été supprimé avec succès"), open=True
                )
                self.data_table.rows = list(self.__products())
                await self.data_table.update_async()
            finally:
                await self.page.update_async()


class EntreeStockView(Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.spacing = 0
        self.list_medocs_entree = ListView(
            auto_scroll=True,
            controls=[],
        )
        self.nom_fournisseur = CustomTextField(
            label="Nom du fournisseur",
            prefix_icon=Icon(Icons.PERSON, color="black"),
            width=350,
            height=50,
        )
        self.quantite = CustomTextField(
            value="1",
            input_filter=NumbersOnlyInputFilter(),
            col=1,
            on_change=self.__update_prix_total,
        )
        self.forme = CustomTextField(col=1)
        self.prix_unitaire_achat = CustomTextField(
            value="0",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=1,
            on_change=self.__update_prix_total,
        )
        self.prix_unitaire_vente = CustomTextField(
            value="0",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=1,
            on_change=self.__update_prix_total,
        )
        self.prix_total_achat = Text("0", weight=FontWeight.BOLD, col=1)
        self.prix_total_vente = Text("0", weight=FontWeight.BOLD, col=1)
        self.benefice = Text("0", weight=FontWeight.BOLD)
        self.totaux_achat = Text("0", weight=FontWeight.BOLD)
        self.totaux_vente = Text("0", weight=FontWeight.BOLD)
        self.totaux_gain = Text("0", weight=FontWeight.BOLD)
        self.gain = Text("0", weight=FontWeight.BOLD)
        self.produit_designation = AutoComplete(
            suggestions=list(self.__autocomplete_suggestions()),
            # on_select=self.__select_medoc_from_suggestion,
        )

        self.controls = [
            Container(
                bgcolor="#f0f0f0",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Row(
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        Text(
                            "Entrée Stock",
                            size=20,
                            weight=FontWeight.BOLD,
                            color="black",
                        ),
                        self.nom_fournisseur,
                    ],
                ),
            ),
            self.__input_medocs(),
            Column(
                scroll=ScrollMode.AUTO,
                controls=[
                    self.list_medocs_entree,
                    Container(
                        bgcolor="#8B8B8B",
                        padding=padding.symmetric(vertical=10, horizontal=20),
                        content=Row(
                            alignment=MainAxisAlignment.END,
                            controls=[
                                Container(
                                    bgcolor="blue",
                                    padding=padding.all(10),
                                    border_radius=border_radius.all(10),
                                    content=Row(
                                        controls=[
                                            Text("TOTAUX ACHAT", color="white"),
                                            self.totaux_achat,
                                            Text("FC", color="white"),
                                        ]
                                    ),
                                ),
                                Container(
                                    bgcolor="blue",
                                    padding=padding.all(10),
                                    border_radius=border_radius.all(10),
                                    content=Row(
                                        controls=[
                                            Text("TOTAUX VENTE", color="white"),
                                            self.totaux_vente,
                                            Text("FC", color="white"),
                                        ]
                                    ),
                                ),
                                Container(
                                    bgcolor="blue",
                                    padding=padding.all(10),
                                    border_radius=border_radius.all(10),
                                    content=Row(
                                        controls=[
                                            Text("TOTAUX GAIN", color="white"),
                                            self.totaux_gain,
                                            Text("FC", color="white"),
                                        ]
                                    ),
                                ),
                                Button(
                                    "Reinitialiser",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="#424242",
                                    ),
                                    on_click=self.__tout_reinitialiser,
                                ),
                                Button(
                                    "Terminer",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="green",
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ]

    def __input_medocs(self):
        return Container(
            padding=padding.symmetric(horizontal=20, vertical=10),
            bgcolor="#CCDEFF",
            content=ResponsiveRow(
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    Text("Produit", col=4),
                    Text("Quantité", col=1),
                    Text("Forme", col=1),
                    Text("PU Achat", col=1),
                    Text("PU Vente", col=1),
                    Text("PT Achat", col=1),
                    Text("PT Vente", col=1),
                    Text("Gain", col=2),
                    Container(
                        padding=padding.only(left=10, right=10, bottom=5),
                        bgcolor="white",
                        border_radius=border_radius.all(10),
                        col=4,
                        height=40,
                        content=self.produit_designation,
                    ),
                    self.quantite,
                    self.forme,
                    self.prix_unitaire_achat,
                    self.prix_unitaire_vente,
                    self.prix_total_achat,
                    self.prix_total_vente,
                    Row(
                        col=2,
                        controls=[
                            Row(
                                expand=True,
                                controls=[
                                    self.gain,
                                    Text("FC"),
                                ],
                            ),
                            Button(
                                "+",
                                elevation=1,
                                style=ButtonStyle(
                                    shape=RoundedRectangleBorder(10),
                                    color="white",
                                    bgcolor="blue",
                                ),
                                on_click=self.add_medoce_panier,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def __autocomplete_suggestions(self):
        for name in list_medocs_names:
            yield AutoCompleteSuggestion(key=name, value=name)

    def add_medoce_panier(self, e):
        # if isinstance(e, list):
        #     self.list_medocs_entree.controls = e
        #     self.list_medocs_entree.update()
        #     self.__reinitialiser_entree()
        if self.produit_designation.selected_index and db.is_medoc_exists(
            self.produit_designation.suggestions[
                self.produit_designation.selected_index
            ].value
        ):
            self.list_medocs_entree.controls.append(
                MedicamentEntree(
                    nom=self.produit_designation.suggestions[
                        self.produit_designation.selected_index
                    ].value,
                    quantite=self.quantite.value,
                    forme=self.forme.value,
                    prix_unitaire_achat=self.prix_unitaire_achat.value,
                    prix_unitaire_vente=self.prix_unitaire_vente.value,
                    prix_total_achat=self.prix_total_achat.value,
                    prix_total_vente=self.prix_total_vente.value,
                    medoc_delete=self.delete_medoc,
                    gain=self.gain.value,
                    calcul_totaux=self.__calcul_totaux,
                )
            )
            self.list_medocs_entree.update()
            self.__reinitialiser_entree()
        else:
            self.page.snack_bar = SnackBar(
                Text("Ce produit n'est pas disponible"), open=True
            )
            self.page.update()
        self.__calcul_totaux()

    def delete_medoc(self, e):
        self.list_medocs_entree.controls.remove(e)
        self.list_medocs_entree.update()
        self.__calcul_totaux()

    def __calcul_totaux(self):
        total_vente = 0
        total_achat = 0
        for medoc in self.list_medocs_entree.controls:
            total_achat += (
                float(medoc.prix_total_achat.value)
                if medoc.prix_total_achat.value
                else 0
            )
            total_vente += (
                float(medoc.prix_total_vente.value)
                if medoc.prix_total_vente.value
                else 0
            )
        self.totaux_achat.value = str(round(total_achat, 3))
        self.totaux_vente.value = str(round(total_vente, 3))
        self.totaux_gain.value = str(round(total_vente - total_achat, 3))
        self.totaux_gain.update()
        self.totaux_achat.update()
        self.totaux_vente.update()

    def __update_prix_total(self, e):
        self.prix_total_achat.value = str(
            round(
                float(
                    self.prix_unitaire_achat.value
                    if self.prix_unitaire_achat.value
                    else 0
                )
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total_achat.update()
        self.prix_total_vente.value = str(
            round(
                float(
                    self.prix_unitaire_vente.value
                    if self.prix_unitaire_vente.value
                    else 0
                )
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total_vente.update()
        self.__calcul_totaux()
        self.gain.value = str(
            round(
                float(self.prix_total_vente.value) - float(self.prix_total_achat.value),
                3,
            )
        )
        self.gain.update()

    def __reinitialiser_entree(self):
        self.quantite.value = ""
        self.forme.value = ""
        self.prix_unitaire_achat.value = ""
        self.prix_unitaire_vente.value = ""
        self.prix_total_vente.value = ""
        self.prix_total_achat.value = ""
        self.gain.value = ""

        self.quantite.update()
        self.forme.update()
        self.prix_unitaire_achat.update()
        self.prix_unitaire_vente.update()
        self.prix_total_vente.update()
        self.prix_total_achat.update()
        self.gain.update()

    def __tout_reinitialiser(self, e):
        self.list_medocs_entree.controls = []
        self.nom_fournisseur.value = ""
        self.totaux_achat.value = ""
        self.totaux_vente.value = ""
        self.totaux_gain.value = ""
        self.totaux_achat.update()
        self.totaux_vente.update()
        self.totaux_gain.update()
        self.__reinitialiser_entree()
        self.__calcul_totaux()
        self.list_medocs_entree.update()

    def __update_prix_total(self, e):
        self.prix_total_achat.value = str(
            round(
                float(
                    self.prix_unitaire_achat.value
                    if self.prix_unitaire_achat.value
                    else 0
                )
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total_achat.update()
        self.prix_total_vente.value = str(
            round(
                float(
                    self.prix_unitaire_vente.value
                    if self.prix_unitaire_vente.value
                    else 0
                )
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total_vente.update()
        self.__calcul_totaux()
        self.gain.value = str(
            round(
                float(self.prix_total_vente.value) - float(self.prix_total_achat.value),
                3,
            )
        )
        self.gain.update()


class PrincipalView(Column):
    def __init__(
        self,
        page: ft.Page,
        draft_handler=None,
        taux_dollar=None,
    ):
        super().__init__()
        self.current_date = datetime.datetime.now()
        self.page = page
        self.taux_dollar = taux_dollar
        self.spacing = 0
        self.draft_handler = draft_handler
        self.list_medocs_panier = ListView(
            auto_scroll=True,
            controls=[],
        )
        self.reduction_accordee = CustomTextField(
            label="Réduction accordée",
            suffix=Text("FC"),
            value=0,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self.__calcul_totaux(),
        )
        self.charges_connexes = CustomTextField(
            label="Charges connexes",
            suffix=Text("FC"),
            value=0,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self.__calcul_totaux(),
        )
        self.page.on_keyboard_event = self.__handler_keyboard_key
        self.nom_client = CustomTextField(
            label="Nom du client",
            prefix_icon=Icon(Icons.PERSON, color="black"),
            width=250,
        )

        self.date_field = CustomTextField(
            label="Date",
            width=160,
            read_only=True,
            value=str(self.current_date.strftime("%d-%m-%Y")),
            prefix_icon=Icon(Icons.CALENDAR_TODAY, color="black"),
            on_click=lambda e: self.page.open(
                DatePicker(
                    first_date=datetime.datetime(year=2010, month=1, day=1),
                    last_date=datetime.datetime(year=2050, month=1, day=1),
                    current_date=self.current_date,
                    cancel_text="Annuler",
                    on_change=self.__select_date,
                )
            ),
        )
        self.totaux = Text(
            "0 Fc",
            color="white",
            weight=FontWeight.BOLD,
        )
        self.devises = Dropdown(
            options=[
                dropdown.Option("FC"),
                dropdown.Option("$"),
            ],
            height=40,
            border_width=0,
            border_radius=10,
            bgcolor="white",
            width=80,
            content_padding=padding.symmetric(vertical=0, horizontal=10),
            value="FC",
            label="Devise",
            on_change=self.__change_devise,
        )
        self.net_a_payer = Text(
            " Net à payer : 0 Fc",
            weight=FontWeight.BOLD,
            color="blue",
        )
        self.previous_devise = self.devises.value
        self.montant_chiffre = Text(
            "Zéro",
            size=12,
            expand=True,
        )
        self.controls = [
            Container(
                bgcolor="#f0f0f0",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Row(
                    controls=[
                        self.nom_client,
                        self.date_field,
                        self.devises,
                        Column(
                            expand=True,
                            spacing=5,
                            controls=[
                                self.net_a_payer,
                                Container(
                                    bgcolor="white",
                                    height=40,
                                    border_radius=border_radius.all(10),
                                    padding=padding.symmetric(vertical=2, horizontal=5),
                                    alignment=alignment.center_left,
                                    content=Row(
                                        controls=[
                                            self.montant_chiffre,
                                            IconButton(
                                                Icons.RECORD_VOICE_OVER,
                                                on_click=lambda e: self.page.run_thread(
                                                    self.__speack
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                        Column(
                            spacing=5,
                            alignment=MainAxisAlignment.CENTER,
                            controls=[
                                Row(
                                    controls=[
                                        Button(
                                            "Réinitialiser",
                                            elevation=1,
                                            style=ButtonStyle(
                                                shape=RoundedRectangleBorder(10),
                                                color="white",
                                                bgcolor="#424242",
                                            ),
                                            on_click=self.__renitialiser_panier,
                                        ),
                                        Button(
                                            "+ Draft",
                                            elevation=1,
                                            style=ButtonStyle(
                                                shape=RoundedRectangleBorder(10),
                                                color="white",
                                                bgcolor="green",
                                            ),
                                            on_click=self.__add_draft,
                                        ),
                                    ],
                                ),
                                Button(
                                    "Terminer",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="blue",
                                    ),
                                    width=170,
                                    on_click=lambda e: self.page.run_task(
                                        self.finaliser_vente
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            self.__input_medoc(),
            Column(
                expand=True,
                scroll=ScrollMode.AUTO,
                controls=[
                    self.list_medocs_panier,
                    Container(
                        padding=padding.symmetric(vertical=10, horizontal=20),
                        content=Column(
                            controls=[
                                Row(
                                    spacing=0,
                                    alignment=MainAxisAlignment.END,
                                    controls=[
                                        Container(
                                            bgcolor="#8B8B8B",
                                            content=Text(
                                                "TOTAUX",
                                                color="white",
                                                weight=FontWeight.BOLD,
                                            ),
                                            padding=padding.all(10),
                                            border_radius=border_radius.only(
                                                top_left=10, bottom_left=10
                                            ),
                                        ),
                                        Container(
                                            bgcolor="blue",
                                            content=self.totaux,
                                            padding=padding.all(10),
                                            border_radius=border_radius.only(
                                                top_right=10, bottom_right=10
                                            ),
                                        ),
                                    ],
                                ),
                                Row(
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        Row(
                                            controls=[
                                                self.charges_connexes,
                                                self.reduction_accordee,
                                            ]
                                        ),
                                        Button(
                                            "Terminer",
                                            elevation=1,
                                            style=ButtonStyle(
                                                shape=RoundedRectangleBorder(10),
                                                color="white",
                                                bgcolor="blue",
                                            ),
                                            width=170,
                                            on_click=lambda e: self.page.run_task(
                                                self.finaliser_vente
                                            ),
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ),
                ],
            ),
        ]

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        self.date_field.update()

    def handler_change_taux(self, taux):
        self.taux_dollar = taux
        if self.devises.value == "$":
            self.previous_devise = "FC"
            self.__change_devise(taux)

    def __change_devise(self, e: ControlEvent | float):
        if self.previous_devise == self.devises.value:
            return
        if isinstance(e, float):
            taux = e
        elif e.data == "$":
            taux = float(self.taux_dollar) if self.taux_dollar else 1
        else:
            taux = 1
        self.prix_unitaire.value = (
            round(float(self.prix_unitaire.value) / taux, 3)
            if self.prix_unitaire.value
            else 0
        )
        self.prix_total.value = (
            round(float(self.prix_total.value) / taux, 3)
            if self.prix_total.value
            else 0
        )
        self.charges_connexes.value = (
            (
                round(float(self.charges_connexes.value) / taux)
                if not (self.charges_connexes.value is None)
                else 0
            )
            if self.devises.value == "$"
            else (
                round(float(self.charges_connexes.value) * float(self.taux_dollar))
                if not (self.charges_connexes.value is None)
                else 0
            )
        )
        self.reduction_accordee.value = (
            (
                round(float(self.reduction_accordee.value) / taux, 3)
                if self.reduction_accordee.value
                else 0
            )
            if self.devises.value == "$"
            else (
                round(float(self.reduction_accordee.value) * float(self.taux_dollar), 3)
                if self.reduction_accordee.value
                else 0
            )
        )
        self.charges_connexes.suffix.value = "$" if self.devises.value == "$" else "FC"
        self.reduction_accordee.suffix.value = (
            "$" if self.devises.value == "$" else "FC"
        )

        self.previous_devise = self.devises.value
        self.prix_unitaire.update()
        self.prix_total.update()
        self.charges_connexes.update()
        self.reduction_accordee.update()
        self.__calcul_totaux()

    def __add_draft(self, e):
        if self.list_medocs_panier.controls:
            self.draft_handler(
                self.list_medocs_panier.controls,
                self.nom_client.value,
                self.date_field.value,
            )
            self.__reinitialiser_entree()
            self.__renitialiser_panier(e)
        self.__calcul_totaux()

    def add_medoce_panier(self, e):
        if isinstance(e, list):
            self.list_medocs_panier.controls = e
            self.list_medocs_panier.update()
            self.__reinitialiser_entree()
            return
        if self.produit_designation.selected_index and db.is_medoc_exists(
            self.produit_designation.suggestions[
                self.produit_designation.selected_index
            ].value
        ):
            self.list_medocs_panier.controls.append(
                Medicament(
                    nom=self.produit_designation.suggestions[
                        self.produit_designation.selected_index
                    ].value,
                    quantite=self.quantite.value if self.quantite.value else 0,
                    forme=self.forme.value,
                    prix_unitaire=(
                        self.prix_unitaire.value if self.prix_unitaire.value else 0
                    ),
                    prix_total=self.prix_total.value,
                    medoc_delete=self.__delete_medoc,
                    calcul_totaux=self.__calcul_totaux,
                )
            )

            self.list_medocs_panier.update()
            self.__reinitialiser_entree()
        else:
            self.page.snack_bar = SnackBar(
                Text("Ce produit n'est pas disponible"), open=True
            )
            self.page.update()
        self.__calcul_totaux()

    def __delete_medoc(self, medoc):
        self.list_medocs_panier.controls.remove(medoc)
        self.list_medocs_panier.update()
        self.__calcul_totaux()

    def __renitialiser_panier(self, e):
        self.list_medocs_panier.controls = []
        self.nom_client.value = ""
        self.date_field.value = str(self.current_date.strftime("%d-%m-%Y"))
        self.list_medocs_panier.update()
        self.nom_client.update()
        self.date_field.update()
        self.__calcul_totaux()
        self.__reinitialiser_entree()
        self.list_medocs_panier.update()

    def __input_medoc(self):
        self.quantite = CustomTextField(
            label="Quantité",
            value="1",
            input_filter=NumbersOnlyInputFilter(),
            col=1,
            on_change=self.__update_prix_total,
            on_click=self.add_medoce_panier,
        )
        self.forme = CustomTextField(
            label="Forme", col=2, on_click=self.add_medoce_panier
        )
        self.prix_unitaire = CustomTextField(
            label="Prix",
            value="0",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=2,
            on_change=self.__update_prix_total,
            on_click=self.add_medoce_panier,
        )
        self.prix_total = Text("0", weight=FontWeight.BOLD)
        self.produit_designation = AutoComplete(
            suggestions=list(self.__autocomplete_suggestions()),
            on_select=self.__select_medoc_from_suggestion,
        )
        self.container_designation = Container(
            padding=padding.only(left=10, right=10, bottom=5),
            bgcolor="white",
            border_radius=border_radius.all(10),
            col=4,
            height=40,
            content=self.produit_designation,
        )

        return Container(
            padding=padding.symmetric(horizontal=20, vertical=10),
            bgcolor="#CCDEFF",
            content=ResponsiveRow(
                controls=[
                    Text("Produit", col=4),
                    Text("Quantité", col=1),
                    Text("Forme", col=2),
                    Text("Prix Unitaire", col=2),
                    Text("Prix total", col=3),
                    self.container_designation,
                    self.quantite,
                    self.forme,
                    self.prix_unitaire,
                    Row(
                        col=3,
                        controls=[
                            Row(
                                expand=True,
                                controls=[
                                    self.prix_total,
                                    Text("FC"),
                                ],
                            ),
                            Button(
                                "+",
                                elevation=1,
                                style=ButtonStyle(
                                    shape=RoundedRectangleBorder(10),
                                    color="white",
                                    bgcolor="blue",
                                ),
                                on_click=self.add_medoce_panier,
                                autofocus=True,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def __autocomplete_suggestions(self):
        for name in list_medocs_names:
            yield AutoCompleteSuggestion(key=name, value=name)

    def __calcul_totaux(self):
        taux = (
            1
            if self.devises.value == "FC"
            else float(self.taux_dollar) if self.taux_dollar else 1
        )
        total = 0
        total_sans_charge_reduc = 0
        for medoc in self.list_medocs_panier.controls:
            total += (
                float(medoc.prix_total.value if medoc.prix_total.value else 0) / taux
            )
            total_sans_charge_reduc += (
                float(medoc.prix_total.value if medoc.prix_total.value else 0) / taux
            )
        total += float(
            self.charges_connexes.value if self.charges_connexes.value else 0
        ) - float(self.reduction_accordee.value if self.reduction_accordee.value else 0)

        self.totaux.value = (
            str(round(total_sans_charge_reduc, 3)) + " FC"
            if self.devises.value == "FC"
            else str(round(total, 3)) + " $"
        )
        self.net_a_payer.value = (
            f"Net à payer : {round(total, 3)} FC"
            if self.devises.value == "FC"
            else f"Net à payer : {round(total, 3)} $"
        )
        total = int(total) if total.is_integer() else round(total, 3)
        self.montant_chiffre.value = number_to_words(total)
        self.net_a_payer.update()
        self.montant_chiffre.update()
        self.totaux.update()

    def __select_medoc_from_suggestion(self, e: AutoCompleteSelectEvent):
        medoc = db.get_medocs_by_name(e.selection.key)
        self.prix_unitaire.value = str(medoc[0][6])
        self.forme.value = medoc[0][11] or ""
        self.prix_total.value = str(
            round(float(self.prix_unitaire.value) * float(self.quantite.value), 3)
        )
        self.prix_unitaire.update()
        self.prix_total.update()
        self.page.update()

    def __update_prix_total(self, e):
        self.prix_total.value = str(
            round(
                float(self.prix_unitaire.value if self.prix_unitaire.value else 0)
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total.update()

    def __reinitialiser_entree(self, e=None):
        self.prix_total.value = "0"
        self.quantite.value = "1"
        self.prix_unitaire.value = "0"
        self.forme.value = ""
        self.charges_connexes.value = "0"
        self.reduction_accordee.value = "0"
        self.produit_designation = AutoComplete(
            suggestions=list(self.__autocomplete_suggestions()),
            on_select=self.__select_medoc_from_suggestion,
        )
        self.container_designation.content = self.produit_designation

        self.charges_connexes.update()
        self.reduction_accordee.update()
        self.prix_total.update()
        self.forme.update()
        self.quantite.update()
        self.prix_unitaire.update()
        self.container_designation.update()

    def __speack(self):
        speaker = Speaker()
        devise = "francs" if self.devises.value == "FC" else "dollars"
        speaker.speaker.setProperty("rate", 210)
        speaker.say(f"Le montant à payer est de {self.montant_chiffre.value} {devise}")

    def load_draft(self, draft_list, nom_client):
        self.list_medocs_panier.controls = draft_list
        self.nom_client.value = nom_client
        self.nom_client.update()
        self.list_medocs_panier.update()
        self.__calcul_totaux()

    async def finaliser_vente(self):
        for medoc in (
            self.list_medocs_panier.controls if self.list_medocs_panier.controls else []
        ):
            medoc_id = db.get_medoc_id_by_name(medoc.nom.value)
            medoc_quantite = db.get_medoc_quantity_by_id(medoc_id)
            if (
                float(medoc_quantite) < float(medoc.quantite.value)
                or medoc_quantite == 0
            ):
                self.page.snack_bar = SnackBar(
                    Text(
                        f"La quantité de {medoc.nom.value} disponible est insuffisante\nIl reste {medoc_quantite} en stock"
                    ),
                    open=True,
                    duration=6000,
                )
                await self.page.update_async()
        num_facture = db.get_last_facture_id() + 1
        for medoc in (
            self.list_medocs_panier.controls if self.list_medocs_panier.controls else []
        ):
            medoc_id = db.get_medoc_id_by_name(medoc.nom.value)
            medoc_quantite = db.get_medoc_quantity_by_id(medoc_id)
            try:
                db.add_new_medoc_to_accounts_mouvement_out(
                    designation=medoc.forme.value or "",
                    qte=int(medoc.quantite.value),
                    pu=float(medoc.prix_unitaire.value),
                    produit_id=medoc_id,
                    pv=float(medoc.prix_total.value),
                )
                db.update_medoc_quantity_by_id(
                    id=medoc_id,
                    new_quantity=round(
                        float(medoc_quantite) - int(medoc.quantite.value)
                    ),
                )
                db.add_to_accounts_mouvement_facture(
                    quantite=int(medoc.quantite.value),
                    forme=medoc.forme.value or "",
                    produit=medoc.nom.value,
                    prix_unitaire=float(medoc.prix_unitaire.value),
                    prix_total=float(medoc.prix_total.value),
                    id_facture=num_facture,
                    nom_client=self.nom_client.value,
                    date=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                )
            except:
                self.page.snack_bar = SnackBar(
                    Text("Une erreur est survenue, veuillez ressayer !"), open=True
                )
                self.page.update()
                return
            else:
                self.page.snack_bar = SnackBar(
                    Text("La vente a été enregistrée avec succès"), open=True
                )
                self.page.update()

        self.imprimer_facture(num_facture)

    def imprimer_facture(self, num_facture):
        liste_medocs_facture = [
            ["N°", "QUANTITE", "FORME", "PRODUIT", "PRIX UNITAIRE", "PRIX TOTAL"]
        ]
        for index, medoc in enumerate(self.list_medocs_panier.controls, start=1):
            liste_medocs_facture.append(
                [
                    str(index),
                    medoc.quantite.value,
                    medoc.forme.value,
                    medoc.nom.value,
                    medoc.prix_unitaire.value,
                    medoc.prix_total.value,
                ]
            )
        facture_thread = Thread(
            target=generer_facture,
            kwargs=dict(
                list_medicaments=liste_medocs_facture,
                prix_total=self.totaux.value + " " + self.devises.value,
                reduction=self.reduction_accordee.value + " " + self.devises.value,
                charges_connexes=self.charges_connexes.value + " " + self.devises.value,
                date=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                nom_client=self.nom_client.value,
                num_facture=num_facture,
                bar_code="F-" + str(num_facture) + "-" + str(self.current_date.year),
                montant_final=self.net_a_payer.value,
                montant_en_lettres=self.montant_chiffre.value
                + " "
                + self.devises.value,
            ),
        )
        facture_thread.start()
        self.__renitialiser_panier(None)

    def __handler_keyboard_key(self, e: KeyboardEvent):
        match e.key:
            case "Escape":
                self.__reinitialiser_entree(None)
            case "Enter":
                self.add_medoce_panier(None)


class Accueil(Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.taux_dollar = CupertinoTextField(
            value="2850",
            width=100,
            keyboard_type=KeyboardType.NUMBER,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
        )
        self.__principal_view = PrincipalView(
            self.page,
            draft_handler=self.__add_draft,
            taux_dollar=self.taux_dollar.value,
        )
        self.__ventes_view = Column()
        self.__clients_view = Column()
        self.current_view = Container(
            content=self.__principal_view, expand=True, expand_loose=True
        )
        self.list_medocs_draft = ListView(
            auto_scroll=True,
            controls=[],
        )
        self.file_picker = FilePicker(on_result=self.__pick_file_db)
        self.page.overlay.append(self.file_picker)
        self.page.update()

        self.content = Row(
            vertical_alignment=CrossAxisAlignment.STRETCH,
            spacing=0,
            controls=[
                Container(
                    bgcolor="#FFFFFF",
                    width=self.page.width * 0.22,
                    content=self._menu(),
                    clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
                    border_radius=border_radius.only(top_right=15),
                ),
                self.current_view,
            ],
        )

    def _menu(self):
        return Column(
            scroll=ScrollMode.AUTO,
            spacing=0,
            expand=True,
            expand_loose=True,
            controls=[
                Container(
                    bgcolor="black",
                    height=110,
                    alignment=alignment.center,
                    content=Row(
                        controls=[
                            Image(
                                src=str(Path(__file__).parent.resolve()).replace(
                                    "\\", "/"
                                )
                                + "/assets/images/logo_shekinah_.png",
                                height=70,
                            ),
                            Text(
                                "Pharmacie\nShekinah",
                                color="white",
                                size=20,
                                text_align=TextAlign.CENTER,
                                weight=FontWeight.BOLD,
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_EVENLY,
                    ),
                ),
                Container(height=10),
                Container(
                    padding=padding.symmetric(horizontal=15),
                    content=Column(
                        controls=[
                            CustomElevatedButton(
                                text="Accueil",
                                icon=Icons.HOME,
                                on_click=self.__change_view,
                            ),
                            CustomElevatedButton(
                                text="Produits",
                                icon=Icons.SHOPPING_CART,
                                on_click=self.__change_view,
                            ),
                            CustomElevatedButton(
                                text="Ventes",
                                icon=Icons.ATTACH_MONEY,
                                on_click=self.__change_view,
                            ),
                            CustomElevatedButton(
                                text="Clients",
                                icon=Icons.PEOPLE,
                                on_click=self.__change_view,
                            ),
                            Container(height=20),
                            Text(
                                "FACTURES ENREGISTREES",
                                color="black",
                            ),
                            self.list_medocs_draft,
                        ],
                    ),
                ),
                Divider(color="black", height=10),
                Container(
                    padding=padding.symmetric(horizontal=15, vertical=10),
                    content=Row(
                        controls=[
                            Text("1$ ="),
                            self.taux_dollar,
                            Text("FC"),
                            IconButton(
                                icon=Icons.CHECK,
                                icon_size=20,
                                icon_color="blue",
                                on_click=self.__change_taux_dollar,
                                padding=padding.all(0),
                            ),
                        ]
                    ),
                ),
                Container(
                    padding=padding.symmetric(horizontal=15, vertical=10),
                    content=Column(
                        controls=[
                            Container(
                                bgcolor="green",
                                width=80,
                                height=40,
                                alignment=alignment.center_right,
                                border_radius=10,
                                padding=padding.all(10),
                                shadow=[
                                    BoxShadow(
                                        color=Colors.with_opacity(0.7, "black"),
                                        blur_radius=1,
                                    )
                                ],
                                content=PopupMenuButton(
                                    expand=True,
                                    content=Text("+ Menu", color="white", size=14),
                                    items=[
                                        PopupMenuItem(
                                            "+ Produits",
                                            on_click=self.__add_new_product,
                                        ),
                                        PopupMenuItem(
                                            "+ Entrée Stock",
                                            on_click=self.__change_view_to_entree_stock,
                                        ),
                                    ],
                                    # icon=Icons.ADD,
                                ),
                            ),
                            CustomElevatedButton(
                                text="Deconnexion",
                                icon=Icons.LOGOUT,
                                on_click=lambda e: self.page.go("/"),
                            ),
                        ],
                    ),
                ),
            ],
        )

    def __change_view_to_entree_stock(self, e):
        self.current_view.content = EntreeStockView(self.page)
        self.current_view.update()

    def __change_view(self, e: ControlEvent):
        match e.control.text:
            case "Accueil":
                self.current_view.content = self.__principal_view
            case "Produits":
                self.current_view.content = ProduitsView(
                    self.page,
                    self.__add_new_product,
                    self.__change_view_to_entree_stock,
                )
            case "Ventes":
                self.current_view.content = VenteView(
                    self.page,
                    self.__add_new_product,
                    self.__change_view_to_entree_stock,
                )
            case "Clients":
                self.current_view.content = self.__clients_view
        self.current_view.update()

    def __change_taux_dollar(self, e):
        if self.taux_dollar.value:
            self.__principal_view.handler_change_taux(float(self.taux_dollar.value))
            self.page.snack_bar = SnackBar(
                content=Text(
                    f"Le taux du dollar a été modifié : 1$ = {self.taux_dollar.value} FC"
                ),
                open=True,
                show_close_icon=True,
            )
            self.page.update()

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        self.date_field.update()

    def __add_new_product(self, e):
        self.nom = CustomTextField(
            label="Nom du produit", height=60, on_blur=self.__verifier_produit
        )
        self.forme = CustomTextField(label="Forme du produit", height=60)
        self.prix_achat = CustomTextField(
            label="Prix d'achat",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            value="0",
            height=60,
        )
        self.prix_vente = CustomTextField(
            label="Prix de vente",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            value="0",
            height=60,
        )
        self.current_date = datetime.datetime.now()
        self.date_field = CustomTextField(
            label="Date d'expiration",
            read_only=True,
            height=60,
            value=str(self.current_date.strftime("%d-%m-%Y")),
            prefix_icon=Icon(Icons.CALENDAR_TODAY, color="black"),
            on_click=lambda e: self.page.open(
                DatePicker(
                    first_date=datetime.datetime(year=2010, month=1, day=1),
                    last_date=datetime.datetime(year=2050, month=1, day=1),
                    current_date=self.current_date,
                    cancel_text="Annuler",
                    on_change=self.__select_date,
                )
            ),
        )
        self.db_file_picked = CustomTextField(
            value=" ", read_only=True, height=40, multiline=True
        )
        self.button_ajouter = Button(
            "Ajouter",
            elevation=1,
            style=ButtonStyle(
                shape=RoundedRectangleBorder(10),
                color="white",
                bgcolor="blue",
            ),
            width=200,
            on_click=lambda e: self.page.run_thread(self.__add_medoc_to_db),
        )
        self.dialog = AlertDialog(
            scrollable=True,
            adaptive=True,
            title=Text("Ajouter un nouveau produit"),
            bgcolor="#f0f0f0",
            content=Column(
                expand=True,
                controls=[
                    self.nom,
                    self.forme,
                    self.prix_achat,
                    self.prix_vente,
                    self.date_field,
                    Text("ou selectionner un fichier de base de données"),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=CrossAxisAlignment.CENTER,
                        controls=[
                            self.db_file_picked,
                            IconButton(
                                icon=Icons.FILE_UPLOAD,
                                bgcolor="#424242",
                                height=40,
                                icon_color="white",
                                on_click=lambda e: self.file_picker.pick_files(
                                    dialog_title="Selectionner un fichier csv de base de données",
                                    allowed_extensions=["csv"],
                                    allow_multiple=False,
                                ),
                            ),
                        ],
                    ),
                ],
            ),
            actions=[
                Button(
                    "Initialiser",
                    elevation=1,
                    style=ButtonStyle(
                        shape=RoundedRectangleBorder(10),
                        color="white",
                        bgcolor="#424242",
                    ),
                    width=200,
                    on_click=self.__renitialiser_produit,
                ),
                self.button_ajouter,
            ],
        )

        self.page.open(self.dialog)
        self.page.update()

    def __pick_file_db(self, result: FilePickerResultEvent):
        try:
            self.db_file_picked.value = result.files[0].name
            self.db_file_picked.update()
            path = result.files[0].path
            db.import_csv_to_db(path)
            self.page.snack_bar = SnackBar(
                Text("Les données du fichier CSV ont été importées avec succès"),
                open=True,
            )
        except Exception as e:
            self.page.snack_bar = SnackBar(
                Text(f"Erreur lors de l'importation du fichier CSV: {e}"), open=True
            )
        finally:
            self.page.update()

    def __add_draft(self, list_draft, nom_client, date):
        self.list_medocs_draft.controls.append(
            CustomDraftButton(
                self.page,
                list_draft,
                nom_client if nom_client else "Inconnu",
                date,
                self.__delete_draft,
                self.__load_draft,
            )
        )
        self.list_medocs_draft.update()

    def __verifier_produit(self, e):
        if self.nom.value:
            if db.is_medoc_exists(self.nom.value.upper()):
                self.button_ajouter.disabled = True
                self.button_ajouter.bgcolor = "#B4B4B4"
                self.nom.error_text = "Ce produit existe déjà"
                self.nom.update()
                self.button_ajouter.update()
            else:
                self.nom.error_text = ""
                self.button_ajouter.disabled = False
                self.button_ajouter.bgcolor = "blue"
                self.button_ajouter.update()
                self.nom.update()

    def __add_medoc_to_db(self):
        if self.db_file_picked.value != " ":
            db.add_medocs_from_csv(self.db_file_picked.value)
            self.page.snack_bar = SnackBar(
                Text("Les produits ont été ajoutés avec succès"), open=True
            )
            self.page.update()
        elif (
            self.nom.value
            and self.forme.value
            and self.prix_achat.value
            and self.prix_vente.value
        ):
            try:
                # "nom",
                # "marque",
                # "date_entree",
                # "date_dexpiration",
                # "prix_achat",
                # "prix_vente",
                self.page.run_thread(
                    db.add_medoc,
                    (
                        self.nom.value.upper(),
                        self.forme.value.upper(),
                        datetime.datetime.now(),
                        datetime.datetime.strptime(
                            self.date_field.value, "%d-%m-%Y"
                        ).date(),
                        float(self.prix_achat.value),
                        float(self.prix_vente.value),
                    ),
                )

            except:
                self.page.snack_bar = SnackBar(
                    Text("Erreur lors de l'ajout du produit"), open=True
                )
            else:
                self.page.snack_bar = SnackBar(
                    Text("Le produit a été ajouté avec succès"), open=True
                )
                self.__renitialiser_produit(None)
            finally:
                self.page.update()

    def __renitialiser_produit(self, e):
        self.nom.value = ""
        self.forme.value = ""
        self.prix_achat.value = "0"
        self.prix_vente.value = "0"
        self.date_field.value = str(self.current_date.strftime("%d-%m-%Y"))
        self.db_file_picked.value = " "
        self.nom.update()
        self.forme.update()
        self.prix_achat.update()
        self.prix_vente.update()
        self.date_field.update()
        self.db_file_picked.update()

    def __delete_draft(self, e):
        self.list_medocs_draft.controls.remove(e)
        self.list_medocs_draft.update()

    def __load_draft(self, e):
        self.__principal_view.load_draft(e.list_medicaments, e.nom_client)
        self.__delete_draft(e)


class VenteView(Column):
    def __init__(
        self, page: ft.Page, handler_entree_produit=None, handler_entree_stock=None
    ):
        super().__init__()
        self.page = page
        self.handler_entree_produit = handler_entree_produit
        self.handler_entree_stock = handler_entree_stock
        self.current_page = 0
        self.items_per_page = 50
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.total_items = len(
            set(invoice[6] for invoice in db.get_all_mouvement_facture())
        )
        self.total_pages = (
            self.total_items + self.items_per_page - 1
        ) // self.items_per_page
        self.search_bar = SearchBar(
            bar_bgcolor="white",
            bar_elevation=1,
            bar_border_side=BorderSide(width=0),
            width=250,
            height=40,
            view_shape=RoundedRectangleBorder(10),
            bar_shape=RoundedRectangleBorder(10),
            bar_hint_text="Rechercher...",
            bar_leading=Icon(Icons.SEARCH, color="black"),
            bar_trailing=[
                IconButton(
                    Icons.CLOSE,
                    icon_color="black",
                    icon_size=18,
                    on_click=lambda e: self.page.run_task(self.__restore_search_bar),
                )
            ],
            on_blur=lambda e: self.page.run_task(self.__search_invoice),
        )
        self.data_table = DataTable(
            expand=True,
            sort_column_index=0,
            heading_row_color={ControlState.DEFAULT: "blue"},
            sort_ascending=True,
            data_row_color={ControlState.HOVERED: "blue"},
            columns=[
                DataColumn(
                    label=Text(
                        "Numéro de Facture",
                        weight=FontWeight.BOLD,
                        color="white",
                    ),
                ),
                DataColumn(
                    label=Text("Nom du Client", weight=FontWeight.BOLD, color="white")
                ),
                DataColumn(
                    label=Text(
                        "Date",
                        weight=FontWeight.BOLD,
                        color="white",
                    )
                ),
                DataColumn(
                    label=Text(
                        "Montant Total",
                        weight=FontWeight.BOLD,
                        color="white",
                    ),
                    numeric=True,
                ),
                DataColumn(
                    label=Text("Actions", weight=FontWeight.BOLD, color="white")
                ),
            ],
            rows=list(self.__invoices()),
        )
        self.controls = [
            Container(
                bgcolor="black",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Row(
                    controls=[
                        Text(
                            "Liste des Factures",
                            color="white",
                            weight=FontWeight.BOLD,
                            size=20,
                        ),
                        Row(
                            controls=[
                                self.search_bar,
                                Button(
                                    "+ Produit",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="blue",
                                    ),
                                    on_click=self.handler_entree_produit,
                                ),
                                Button(
                                    "+ Entrée Stock",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="blue",
                                    ),
                                    on_click=self.handler_entree_stock,
                                ),
                                Button(
                                    " ",
                                    elevation=1,
                                    style=ButtonStyle(
                                        shape=RoundedRectangleBorder(10),
                                        color="white",
                                        bgcolor="white",
                                    ),
                                    icon=Icons.LOOP,
                                    icon_color="blue",
                                ),
                            ],
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
            Container(
                expand=True,
                padding=padding.symmetric(horizontal=10, vertical=10),
                content=Column(
                    expand=True,
                    horizontal_alignment=CrossAxisAlignment.STRETCH,
                    scroll=ScrollMode.AUTO,
                    controls=[self.data_table],
                ),
            ),
            Row(
                alignment=MainAxisAlignment.CENTER,
                controls=[
                    Button(
                        "Page Précédente",
                        on_click=self.__previous_page,
                        disabled=self.current_page == 0,
                        elevation=1,
                        style=ButtonStyle(
                            shape=RoundedRectangleBorder(10),
                            color="white",
                            bgcolor="blue",
                        ),
                    ),
                    Text(f"Page {self.current_page + 1} sur {self.total_pages}"),
                    Button(
                        "Page Suivante",
                        on_click=self.__next_page,
                        disabled=self.current_page >= self.total_pages - 1,
                        elevation=1,
                        style=ButtonStyle(
                            shape=RoundedRectangleBorder(10),
                            color="white",
                            bgcolor="blue",
                        ),
                    ),
                ],
            ),
        ]

    async def __restore_search_bar(self):
        self.search_bar.value = ""
        self.search_bar.update()
        self.data_table.rows = list(self.__invoices())
        await self.data_table.update_async()

    async def __search_invoice(self):
        invoices_found = db.get_all_mouvement_facture_by_id_facture(
            self.search_bar.value
        )
        if invoices_found:
            self.data_table.rows = list(self.__invoices_searched(invoices_found))
            await self.data_table.update_async()
        else:
            self.page.snack_bar = SnackBar(Text("Aucune facture trouvée"), open=True)
        await self.page.update_async()

    def __invoices_searched(self, invoices_found):
        unique_invoices = {}
        for invoice in invoices_found:
            if invoice[6] not in unique_invoices:
                unique_invoices[invoice[6]] = invoice
        for invoice in unique_invoices.values():
            yield DataRow(
                cells=[
                    DataCell(Text(invoice[6])),
                    DataCell(Text(invoice[7])),
                    DataCell(Text(invoice[8])),
                    DataCell(Text(invoice[5])),
                    DataCell(
                        IconButton(
                            Icons.PRINT,
                            icon_color="blue",
                            on_click=lambda e, invoice_id=invoice[
                                6
                            ]: self.__print_invoice(invoice_id),
                        )
                    ),
                ]
            )

    def __invoices(self):
        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        invoices = db.get_all_mouvement_facture()[start_index:end_index]
        unique_invoices = {}
        for invoice in invoices:
            if invoice[6] not in unique_invoices:
                unique_invoices[invoice[6]] = {"invoice": invoice, "total": 0}
            unique_invoices[invoice[6]]["total"] += float(invoice[5])
        for invoice_data in unique_invoices.values():
            invoice = invoice_data["invoice"]
            total = invoice_data["total"]
            yield DataRow(
                cells=[
                    DataCell(Text(invoice[6])),
                    DataCell(Text(invoice[7])),
                    DataCell(Text(invoice[8])),
                    DataCell(Text(str(total))),
                    DataCell(
                        IconButton(
                            Icons.PRINT,
                            icon_color="blue",
                            on_click=lambda e, invoice_id=invoice[
                                6
                            ]: self.__print_invoice(invoice_id),
                        )
                    ),
                ]
            )

    def __next_page(self, e):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.__update_table()

    def __previous_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
            self.__update_table()

    def __update_table(self):
        self.data_table.rows = list(self.__invoices())
        self.controls[-1].controls[
            1
        ].value = f"Page {self.current_page + 1} sur {self.total_pages}"
        self.controls[-1].controls[0].disabled = self.current_page == 0
        self.controls[-1].controls[2].disabled = (
            self.current_page >= self.total_pages - 1
        )
        self.data_table.update()
        self.page.update()

    def __print_invoice(self, invoice_id):
        # Implement the logic to print the invoice using the invoice_id
        list_medocs = db.get_all_mouvement_facture_by_id_facture(invoice_id)
        nom_client = list_medocs[0][7]
        date = list_medocs[0][8]
        montant_total = 0
        for medoc in list_medocs:
            montant_total += float(medoc[5])
        liste_medocs_facture = [
            ["N°", "QUANTITE", "FORME", "PRODUIT", "PRIX UNITAIRE", "PRIX TOTAL"]
        ]
        for index, medoc in enumerate(list_medocs, start=1):
            liste_medocs_facture.append(
                [
                    str(index),
                    medoc[4],
                    medoc[3],
                    medoc[2],
                    medoc[5],
                    medoc[5],
                ]
            )
        facture_thread = Thread(
            target=generer_facture,
            kwargs=dict(
                list_medicaments=liste_medocs_facture,
                prix_total=str(montant_total) + " FC",
                reduction="0 FC",
                charges_connexes="0 FC",
                date=date,
                nom_client=nom_client,
                num_facture=invoice_id,
                bar_code="F-"
                + str(invoice_id)
                + "-"
                + str(datetime.datetime.now().year),
                montant_final="Net à payer : " + str(montant_total) + " FC",
                montant_en_lettres=number_to_words(montant_total) + " FC",
            ),
        )
        facture_thread.start()


def main(page: ft.Page):
    def on_route_change(route: RouteChangeEvent):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    LoginView(page),
                ],
                padding=padding.all(0),
            )
        )
        if page.route == "/home":
            page.views.append(
                ft.View(
                    "/home",
                    [
                        Accueil(page),
                    ],
                    padding=padding.all(0),
                )
            )
        page.update()

    def on_view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    def yes_click(e):
        page.window.destroy()
        # page.update()

    def no_click(e):
        page.close(confirm_dialog)

    page.padding = padding.all(0)
    page.title = "Shekinah App"
    page.bgcolor = "#f0f0f0"
    page.fonts = {
        "Poppins": str(Path(__file__).parent.resolve()).replace("\\", "/")
        + "/assets/fonts/Poppins/Poppins-Regular.ttf",
    }
    page.theme = Theme(font_family="Poppins")
    page.window.center()
    page.window.maximized = True
    # page.window.prevent_close = True
    # page.window.on_event = handle_window_event

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Veuillez confirmer"),
        content=ft.Text("Voulez-vous quitter ?"),
        actions=[
            ft.ElevatedButton("Oui, quitter", on_click=yes_click),
            ft.OutlinedButton("Non, annuler", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.go(page.route)


ft.app(
    main,
    assets_dir=str(Path(__file__).parent.resolve()).replace("\\", "/") + "/assets",
)
