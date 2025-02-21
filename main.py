import datetime
from components.CustomElevatedButton import CustomElevatedButton
from components.CustomDraftButton import CustomDraftButton
from components.CustomTextField import CustomTextField
from utils.nombre_to_chiffre import number_to_words
from models.medicament_entree import MedicamentEntree
from utils.impression_facture import generer_facture
from views.login_view import LoginView
from models.medicament import Medicament
import pickle
from pathlib import Path
from utils.speaker import Speaker
from db.db_utils import DBUtils
from threading import Thread
from flet import (
    Row,
    Column,
    Container,
    Text,
    Icon,
    IconButton,
    Button,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    SearchBar,
    BorderSide,
    RoundedRectangleBorder,
    ControlState,
    MainAxisAlignment,
    FontWeight,
    ScrollMode,
    alignment,
    padding,
    border_radius,
    Colors,
    BoxShadow,
    ClipBehavior,
    CupertinoTextField,
    KeyboardType,
    InputFilter,
    NumbersOnlyInputFilter,
    AutoComplete,
    AutoCompleteSuggestion,
    AutoCompleteSelectEvent,
    DatePicker,
    ControlEvent,
    Dropdown,
    dropdown,
    Image,
    TextAlign,
    SnackBar,
    FilePicker,
    FilePickerResultEvent,
    PopupMenuButton,
    PopupMenuItem,
    Divider,
    Theme,
    RouteChangeEvent,
    AlertDialog,
    MainAxisAlignment,
    CrossAxisAlignment,
    ResponsiveRow,
    ListView,
    KeyboardEvent,
    Icons,
    ButtonStyle,
    Page,
    app,
    ElevatedButton,
    OutlinedButton,
    View,
    Badge,
    Switch,
)

# import logging

# logging.basicConfig(level=logging.DEBUG)


current_directory = (
    str(Path(__file__).parent.resolve()).replace("\\", "/")
    + "/assets/db/db_test.sqlite3"
)

drafts_directory = (
    str(Path(__file__).parent.resolve()).replace("\\", "/") + "/assets/drafts/drafts.df"
)


db = DBUtils(current_directory)
# list_medocs_names = db.get_all_medocs_list()
# list_medocs_for_preview = db.get_medocs_for_list_preview()


def init_load_drafts():
    try:
        with open(drafts_directory, "rb") as f:
            drafts = pickle.load(f)
    except (FileNotFoundError, pickle.UnpicklingError) as e:
        print(f"Error loading drafts: {e}")
        drafts = []
    return drafts


def save_drafts(drafts):
    try:
        with open(drafts_directory, "wb") as f:
            pickle.dump(drafts, f)
    except (FileNotFoundError, pickle.PicklingError) as e:
        print(f"Error saving drafts: {e}")


class ProduitsView(Column):
    def __init__(
        self, page: Page, handler_entree_produit=None, handler_entree_stock=None
    ):
        super().__init__()
        self.page = page
        self.handler_entree_produit = handler_entree_produit
        self.handler_entree_stock = handler_entree_stock
        self.current_page = 0
        self.expand = True
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.items_per_page = 50
        self.all_medocs_for_preview = db.get_medocs_for_list_preview()
        self.total_items = len(self.all_medocs_for_preview)
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
                    on_click=lambda e: self.__restore_search_bar(),
                )
            ],
            on_blur=lambda e: self.__search_medoc(),
        )
        self.data_table = DataTable(
            expand=True,
            sort_ascending=True,
            sort_column_index=0,
            heading_row_color={ControlState.DEFAULT: "blue"},
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
                                    height=40,
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
                                    height=40,
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
                                    height=40,
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
                    scroll=ScrollMode.ALWAYS,
                    expand=True,
                    horizontal_alignment=CrossAxisAlignment.STRETCH,
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
                        height=40,
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
                        height=40,
                    ),
                ],
            ),
        ]

    def __restore_search_bar(self):
        self.search_bar.value = ""
        try:
            self.search_bar.update()
        except Exception as e:
            print(f"Error updating search bar: {e}")
        self.data_table.rows = list(self.__products())
        try:
            self.data_table.update()
        except Exception as e:
            print(f"Error updating data table: {e}")

    def __search_medoc(self):
        try:
            products_founds = db.get_medocs_for_list_preview_by_containing_name(
                self.search_bar.value
            )
            if products_founds:
                self.data_table.rows = list(self.__products_searched(products_founds))
                try:
                    self.data_table.update()
                except Exception as e:
                    print(f"Error updating data table: {e}")
            else:
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Aucun produit trouvé"), open=True)
                )
            self.page.update()
        except Exception as e:
            print(f"Error searching medoc: {e}")

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
                    DataCell(Text(medoc[2]), visible=False),
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
        for medoc in self.all_medocs_for_preview[start_index:end_index]:
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
                    DataCell(Text(medoc[2]), visible=False),
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
        try:
            self.data_table.update()
        except Exception as e:
            print(f"Error updating data table: {e}")
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

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
            height=40,
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
                    height=40,
                ),
                self.button_mettre_a_jour,
            ],
        )

        self.page.open(self.dialog)
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        try:
            self.date_field.update()
        except Exception as e:
            print(f"Error updating date field: {e}")

    def __update_medoc_accounts_produit_db(self):
        self.page.run_thread(self.__update_medoc_accounts_produit_db_async)

    def __update_medoc_accounts_produit_db_async(self):
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
                self.all_medocs_for_preview = db.get_medocs_for_list_preview()
            except Exception as e:
                print(f"Error updating medoc: {e}")
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(
                        Text("Une erreur est survenue, veuillez ressayer !"), open=True
                    )
                )
            else:
                self.page.close(self.dialog)
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Le produit a été modifié avec succès"), open=True)
                )
                self.data_table.rows = list(self.__products())
                try:
                    self.data_table.update()
                except Exception as e:
                    print(f"Error updating data table: {e}")
            finally:
                try:
                    self.page.update()
                except Exception as e:
                    print(f"Error updating page: {e}")

    def __delete_medoc_accounts_produit_db(self):
        self.page.run_thread(self.__delete_medoc_accounts_produit_db_async)

    def __delete_medoc_accounts_produit_db_async(self):
        if self.nom.value:
            try:
                db.delete_medoc(self.nom.value)
                self.all_medocs_for_preview = db.get_medocs_for_list_preview()
            except Exception as e:
                print(f"Error deleting medoc: {e}")
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(
                        Text("Une erreur est survenue, veuillez ressayer !"), open=True
                    )
                )
            else:

                self.page.close(self.dialog)
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Le produit a été supprimé avec succès"), open=True)
                )
                self.data_table.rows = list(self.__products())
                try:
                    self.data_table.update()
                except Exception as e:
                    print(f"Error updating data table: {e}")
            finally:
                try:
                    self.page.update()
                except Exception as e:
                    print(f"Error updating page: {e}")


class EntreeStockView(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.spacing = 0
        self.list_all_medocs_db = db.get_all_medocs_list()
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
            suffix=Column(
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=0,
                tight=True,
                controls=[
                    IconButton(
                        icon=Icons.ARROW_DROP_UP,
                        icon_color="black",
                        icon_size=20,
                        padding=padding.all(0),
                        height=15,
                        width=20,
                        on_click=self.__incrise_quantite,
                    ),
                    IconButton(
                        icon=Icons.ARROW_DROP_DOWN,
                        icon_color="black",
                        icon_size=20,
                        padding=padding.all(0),
                        height=15,
                        width=20,
                        on_click=self.__desincrise_quantite,
                    ),
                ],
            ),
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
                scroll=ScrollMode.ALWAYS,
                expand=True,
                auto_scroll=True,
                controls=[
                    self.list_medocs_entree,
                ],
            ),
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
                            height=40,
                        ),
                        Button(
                            "Terminer",
                            elevation=1,
                            style=ButtonStyle(
                                shape=RoundedRectangleBorder(10),
                                color="white",
                                bgcolor="green",
                            ),
                            height=40,
                            on_click=lambda e: self.page.run_thread(
                                self.__finaliser_entree_medocs
                            ),
                        ),
                    ],
                ),
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
                    self.container_designation,
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
                                height=40,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def __incrise_quantite(self, e):
        self.quantite.value = (
            str(int(self.quantite.value) + 1) if self.quantite.value else 1
        )
        try:
            self.quantite.update()
        except Exception as e:
            print(f"Error updating quantite: {e}")
        self.__update_prix_total(None)

    def __desincrise_quantite(self, e):
        if self.quantite.value and int(self.quantite.value) > 0:
            self.quantite.value = str(int(self.quantite.value) - 1)
        else:
            self.quantite.value = "0"
        try:
            self.quantite.update()
        except Exception as e:
            print(f"Error updating quantite: {e}")
        self.__update_prix_total(None)

    def __autocomplete_suggestions(self):
        for name in self.list_all_medocs_db:
            yield AutoCompleteSuggestion(key=name, value=name)

    def __select_medoc_from_suggestion(self, e: AutoCompleteSelectEvent):
        medoc = db.get_medocs_by_name(e.selection.key)
        self.prix_unitaire_vente.value = str(medoc[0][6])
        self.prix_unitaire_achat.value = str(medoc[0][4])
        self.forme.value = medoc[0][11] or ""
        self.prix_total_vente.value = (
            str(
                round(
                    float(self.prix_unitaire_vente.value) * float(self.quantite.value),
                    3,
                )
            )
            or "0"
        )
        self.prix_total_achat.value = (
            str(
                round(
                    float(self.prix_unitaire_achat.value) * float(self.quantite.value),
                    3,
                )
            )
            or "0"
        )
        try:
            self.prix_unitaire_achat.update()
            self.prix_total_achat.update()
            self.prix_unitaire_vente.update()
            self.prix_total_vente.update()
            self.page.update()
        except Exception as e:
            print(f"Error updating fields: {e}")
        self.__update_prix_total(None)

    def add_medoce_panier(self, e):
        # if isinstance(e, list):
        #     self.list_medocs_entree.controls = e
        #     self.list_medocs_entree.update()
        #     self.__reinitialiser_entree()
        if (
            self.produit_designation.selected_index == 0
            or self.produit_designation.selected_index
        ) and db.is_medoc_exists(
            self.produit_designation.suggestions[
                self.produit_designation.selected_index
            ].value
        ):
            try:
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
                        calcul_totaux=self._calcul_totaux,
                    )
                )
                try:
                    self.list_medocs_entree.update()
                except Exception as e:
                    print(f"Error updating list_medocs_entree: {e}")
                self.__reinitialiser_entree()
            except Exception as e:
                print(f"Error while adding medoc in panier entree stock : {e}")
        else:
            return
        self._calcul_totaux()

    def delete_medoc(self, e):
        self.list_medocs_entree.controls.remove(e)
        try:
            self.list_medocs_entree.update()
        except Exception as e:
            print(f"Error updating list_medocs_entree: {e}")
        self._calcul_totaux()

    def _calcul_totaux(self):
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
        try:
            self.totaux_gain.update()
            self.totaux_achat.update()
            self.totaux_vente.update()
        except Exception as e:
            print(f"Error updating totals: {e}")

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
        self._calcul_totaux()
        self.gain.value = str(
            round(
                float(self.prix_total_vente.value) - float(self.prix_total_achat.value),
                3,
            )
        )
        try:
            self.gain.update()
        except Exception as e:
            print(f"Error updating price fields: {e}")

    def __reinitialiser_entree(self):
        self.quantite.value = "1"
        self.forme.value = " "
        self.prix_unitaire_achat.value = "0"
        self.prix_unitaire_vente.value = "0"
        self.prix_total_vente.value = "0"
        self.prix_total_achat.value = "0"
        self.gain.value = "0"
        self.produit_designation = AutoComplete(
            suggestions=list(self.__autocomplete_suggestions()),
            on_select=self.__select_medoc_from_suggestion,
        )
        self.container_designation.content = self.produit_designation

        try:
            self.quantite.update()
            self.forme.update()
            self.prix_unitaire_achat.update()
            self.prix_unitaire_vente.update()
            self.prix_total_vente.update()
            self.prix_total_achat.update()
            self.container_designation.update()
            self.gain.update()
        except Exception as e:
            print(f"Error updating fields: {e}")

    def __tout_reinitialiser(self, e):
        self.list_medocs_entree.controls = []
        self.nom_fournisseur.value = ""
        self.totaux_achat.value = ""
        self.totaux_vente.value = ""
        self.totaux_gain.value = ""
        try:
            self.totaux_achat.update()
            self.totaux_vente.update()
            self.totaux_gain.update()
        except Exception as e:
            print(f"Error updating totals: {e}")
        self.__reinitialiser_entree()
        self._calcul_totaux()
        try:
            self.list_medocs_entree.update()
        except Exception as e:
            print(f"Error updating list_medocs_entree: {e}")

    def __finaliser_entree_medocs(self):
        if not self.list_medocs_entree.controls:
            return
        names_medocs = []
        quantities_medocs = []
        for medoc in (
            self.list_medocs_entree.controls if self.list_medocs_entree.controls else []
        ):
            medoc_quantite = db.get_medoc_quantity_by_name(medoc.nom.value)
            try:
                names_medocs.append(medoc.nom.value)
                quantities_medocs.append(
                    int(float(medoc_quantite or 0) + float(medoc.quantite.value or 0))
                )
                db.add_new_medoc_to_accounts_mouvement_in(
                    designation=medoc.forme.value or "",
                    qte=int(medoc.quantite.value),
                    pu=float(medoc.prix_unitaire_vente.value),
                    produit_id=db.get_medoc_id_by_name(medoc.nom.value),
                    pv=float(medoc.prix_total_vente.value),
                )
            except Exception as e:
                print(e)
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(
                        Text("Une erreur est survenue, veuillez ressayer !"), open=True
                    )
                )
                self.page.update()
                return
        if self.page.overlay:
            self.page.overlay.clear()
        self.page.overlay.append(
            SnackBar(Text("L'entrée a été effectuée avec succès !"), open=True)
        )
        self.page.update()

        self.page.run_thread(
            db.update_medocs_quantities, names_medocs, quantities_medocs
        )
        self.__tout_reinitialiser(None)

    def handler_keyboard_key(self, e: KeyboardEvent):
        try:
            if self.page:
                match e.key:
                    case "Escape":
                        self.__reinitialiser_entree()
                    case "Enter":
                        self.add_medoce_panier(None)
        except Exception as e:
            print(e)


class PrincipalView(Column):
    def __init__(
        self,
        page: Page,
        draft_handler=None,
        taux_dollar=None,
    ):
        super().__init__()
        self.current_date = datetime.datetime.now()
        self.page = page
        self.taux_dollar = taux_dollar
        self.spacing = 0
        self.list_all_medocs_db = db.get_all_medocs_list()
        self.draft_handler = draft_handler
        self.list_medocs_panier = ListView(
            auto_scroll=True,
            controls=[],  # self.__medocs_panier(),
            build_controls_on_demand=True,
        )
        self.reduction_accordee = CustomTextField(
            label="Réduction accordée",
            suffix=Text("FC"),
            value=0,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self._calcul_totaux(),
        )
        self.charges_connexes = CustomTextField(
            label="Charges connexes",
            suffix=Text("FC"),
            value=0,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            on_change=lambda e: self._calcul_totaux(),
        )
        self.page.on_keyboard_event = self.handler_keyboard_key
        self.change_devise_medoc = None
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
        self.switch_speaker = Switch(value=False)
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
                                            self.switch_speaker,
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
                                            height=40,
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
                                            height=40,
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
                                    on_click=lambda e: self.page.run_thread(
                                        self.finaliser_vente
                                    ),
                                    height=40,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
            self.__input_medoc(),
            Column(
                expand=True,
                scroll=ScrollMode.ALWAYS,
                auto_scroll=True,
                controls=[
                    self.list_medocs_panier,
                ],
            ),
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
                                    on_click=lambda e: self.page.run_thread(
                                        self.finaliser_vente
                                    ),
                                    height=40,
                                ),
                            ],
                        ),
                    ]
                ),
            ),
        ]

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        try:
            self.date_field.update()
        except Exception as e:
            print(f"Error updating date field: {e}")

    def handler_change_taux(self, taux):
        self.taux_dollar = taux

    def __change_devise(self, e: ControlEvent | float):
        if self.previous_devise == self.devises.value:
            return
        if e.data == "$":
            taux = float(self.taux_dollar) if self.taux_dollar else 1
        elif e.data == "FC":
            taux = 1 / float(self.taux_dollar) if self.taux_dollar else 1
        else:
            taux = 1
        for medoc in self.list_medocs_panier.controls or []:
            medoc.handler_devise_change(self.devises.value, taux)
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
        try:
            self.prix_unitaire.update()
            self.prix_total.update()
            self.charges_connexes.update()
            self.reduction_accordee.update()
        except Exception as e:
            print(f"Error updating fields: {e}")
        self._calcul_totaux()

    def __add_draft(self, e):
        if self.list_medocs_panier.controls:
            self.draft_handler(
                self.list_medocs_panier.controls,
                self.nom_client.value,
                self.date_field.value,
            )
            draft_lists = init_load_drafts()
            draft = []

            for medoc in self.list_medocs_panier.controls:
                draft.append(
                    (
                        medoc.nom.value or "",
                        medoc.quantite.value or 0,
                        medoc.forme.value or "",
                        medoc.prix_unitaire.value or 0,
                        medoc.prix_total.value or 0,
                        self.nom_client.value or "",
                        self.date_field.value or "",
                        self.devises.value or "FC",
                    )
                )
            draft_lists.append(draft)
            self.page.run_thread(save_drafts, draft_lists)
            try:
                self.__reinitialiser_entree()
                self.__renitialiser_panier(e)
            except Exception as e:
                print(f"Error resetting entry or cart: {e}")
        self._calcul_totaux()

    def add_medoce_panier(self, e):
        if isinstance(e, list):
            self.list_medocs_panier.controls = e
            try:
                self.list_medocs_panier.update()
            except Exception as e:
                print(f"Error updating list_medocs_panier: {e}")

            self.__reinitialiser_entree()
            return
        if (not isinstance(self.produit_designation.selected_index, int)) or (
            self.produit_designation.selected_index is None
        ):
            return
        if (
            isinstance(self.produit_designation.selected_index, int)
            and (
                self.produit_designation.selected_index == 0
                or self.produit_designation.selected_index
            )
            and db.is_medoc_exists(
                self.produit_designation.suggestions[
                    self.produit_designation.selected_index
                ].value
            )
        ):
            try:
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
                        medoc_delete=self._delete_medoc,
                        calcul_totaux=self._calcul_totaux,
                        devise_initiale=self.devises.value or "FC",
                    )
                )
                try:
                    self.list_medocs_panier.update()
                except Exception as e:
                    print(f"Error updating list_medocs_panier: {e}")
                    # Copier les cotroles de la liste dans une nouvelle liste
                    # try:
                    #     self.list_medocs_panier = ListView(
                    #         expand=True,
                    #         controls=self.list_medocs_panier.controls,
                    #     )
                    # except Exception as e:
                    #     print(f"Error updating and changing list_medocs_panier: {e}")

            except Exception as e:
                print(e)
            else:
                self.__reinitialiser_entree()
                self._calcul_totaux()
        else:
            return

    def _delete_medoc(self, medoc):
        self.list_medocs_panier.controls.remove(medoc)
        try:
            self.list_medocs_panier.update()
        except Exception as e:
            print(f"Error updating list_medocs_panier: {e}")
        self._calcul_totaux()

    def __renitialiser_panier(self, e):
        self.list_medocs_panier.controls = []
        self.nom_client.value = ""
        self.date_field.value = str(self.current_date.strftime("%d-%m-%Y"))
        try:
            self.list_medocs_panier.update()
            self.nom_client.update()
            self.date_field.update()
        except Exception as e:
            print(f"Error updating fields: {e}")
        self._calcul_totaux()
        try:
            self.list_medocs_panier.update()
        except Exception as e:
            print(f"Error updating list_medocs_panier: {e}")

    def __input_medoc(self):
        self.quantite = CustomTextField(
            value="1",
            input_filter=NumbersOnlyInputFilter(),
            col=1,
            on_change=self.__update_prix_total,
            suffix=Column(
                alignment=MainAxisAlignment.START,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=0,
                tight=True,
                controls=[
                    IconButton(
                        icon=Icons.ARROW_DROP_UP,
                        icon_color="black",
                        icon_size=20,
                        padding=padding.all(0),
                        height=15,
                        width=20,
                        on_click=lambda e: self.__update_prix_total("incrise"),
                    ),
                    IconButton(
                        icon=Icons.ARROW_DROP_DOWN,
                        icon_color="black",
                        icon_size=20,
                        padding=padding.all(0),
                        height=15,
                        width=20,
                        on_click=lambda e: self.__update_prix_total("desincrise"),
                    ),
                ],
            ),
        )
        self.forme = CustomTextField(
            label="Forme", col=2,
        )
        self.prix_unitaire = CustomTextField(
            label="Prix",
            value="0",
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=2,
            on_change=self.__update_prix_total,
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
                                    Text(self.devises.value or "FC"),
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
                                height=40,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def __autocomplete_suggestions(self):
        for name in self.list_all_medocs_db:
            yield AutoCompleteSuggestion(key=name, value=name)

    def _calcul_totaux(self):
        total = 0
        total_sans_charge_reduc = 0
        for medoc in self.list_medocs_panier.controls:
            total += float(medoc.prix_total.value if medoc.prix_total.value else 0)

            total_sans_charge_reduc += float(
                medoc.prix_total.value if medoc.prix_total.value else 0
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
        try:
            self.net_a_payer.update()
            self.montant_chiffre.update()
            self.totaux.update()
        except Exception as e:
            print(f"Error updating totals: {e}")

    def __select_medoc_from_suggestion(self, e: AutoCompleteSelectEvent):
        medoc = db.get_medocs_by_name(e.selection.key)
        if not medoc:
            return
        prix = (
            (float(medoc[0][6]) / float(self.taux_dollar) or 0)
            if self.devises.value == "$"
            else float(medoc[0][6])
        )  # prix de vente
        self.prix_unitaire.value = str(round(prix, 3) or "0")
        self.forme.value = medoc[0][11] or ""
        self.prix_total.value = str(
            round(float(self.prix_unitaire.value) * float(self.quantite.value), 3)
        )
        try:
            self.prix_unitaire.update()
            self.prix_total.update()
        except Exception as e:
            print(f"Error updating price fields: {e}")
        # self.page.update()

    def __update_prix_total(self, e):
        if e == "incrise":
            self.quantite.value = (
                str(int(self.quantite.value) + 1) if self.quantite.value else 1
            )
            try:
                self.quantite.update()
            except Exception as e:
                print(f"Error updating quantite: {e}")
        elif e == "desincrise":
            if self.quantite.value and int(self.quantite.value) > 0:
                self.quantite.value = str(int(self.quantite.value) - 1)
            else:
                self.quantite.value = "0"
            try:
                self.quantite.update()
            except Exception as e:
                print(f"Error updating quantite: {e}")

        self.prix_total.value = str(
            round(
                float(self.prix_unitaire.value if self.prix_unitaire.value else 0)
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        try:
            self.prix_total.update()
        except Exception as e:
            print(f"Error updating price fields: {e}")

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

        try:
            self.charges_connexes.update()
            self.reduction_accordee.update()
            self.prix_total.update()
            self.forme.update()
            self.quantite.update()
            self.prix_unitaire.update()
            self.container_designation.update()
        except Exception as e:
            print(f"Error updating fields: {e}")

    def reinitialiser_entree_produit_new(self):
        self.produit_designation = AutoComplete(
            suggestions=list(self.__autocomplete_suggestions()),
            on_select=self.__select_medoc_from_suggestion,
        )
        self.container_designation.content = self.produit_designation
        try:
            self.container_designation.update()
        except Exception as e:
            print(f"Error updating container_designation on add new product : {e}")

    def __speack(self):
        speaker = Speaker()
        devise = "francs" if self.devises.value == "FC" else "dollars"
        speaker.speaker.setProperty("rate", 210)
        speaker.say(f"Le montant à payer est de {self.montant_chiffre.value} {devise}")

    def __speack_with_args(self, text: str, devise: str):
        speaker = Speaker()
        speaker.speaker.setProperty("rate", 210)
        speaker.say(f"Le montant à payer est de {text} {devise}")

    def load_draft(self, draft_list, nom_client):
        self.list_medocs_panier.controls = draft_list
        if self.devises.value != draft_list[0].devise.value:
            self.devises.value = draft_list[0].devise.value
            self.previous_devise = draft_list[0].devise.value
        self.nom_client.value = nom_client
        try:
            self.nom_client.update()
            self.devises.update()
            self.list_medocs_panier.update()
        except Exception as e:
            print(f"Error updating fields: {e}")
        self._calcul_totaux()

    def finaliser_vente(self):
        if not self.list_medocs_panier.controls:
            return

        num_facture = db.get_last_facture_id() + 1
        names_medocs = []
        quantities_medocs = []
        for medoc in (
            self.list_medocs_panier.controls if self.list_medocs_panier.controls else []
        ):

            medoc_quantite = db.get_medoc_quantity_by_name(medoc.nom.value)
            try:
                names_medocs.append(medoc.nom.value)
                quantities_medocs.append(
                    int(float(medoc_quantite or 0) - float(medoc.quantite.value or 0))
                )
                db.add_to_accounts_mouvement_facture(
                    quantite=int(medoc.quantite.value) or 0,
                    forme=medoc.forme.value or " ",
                    produit=medoc.nom.value,
                    prix_unitaire=round(float(medoc.prix_unitaire.value), 3) or 0,
                    prix_total=round(float(medoc.prix_total.value), 3) or 0,
                    id_facture=num_facture,
                    nom_client=self.nom_client.value,
                    date=self.date_field.value+datetime.datetime.now().strftime(" %H:%M:%S"),
                    devise=self.devises.value,
                    reductions=round(float(self.reduction_accordee.value), 3) or 0.0,
                    charges_connexes=round(float(self.charges_connexes.value), 3)
                    or 0.0,
                )
            except:
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(
                        Text("Une erreur est survenue, veuillez ressayer !"), open=True
                    )
                )
                try:
                    self.page.update()
                except Exception as e:
                    print(f"Error updating page in finaliser facture: {e}")
                return
        self.page.run_thread(
            db.update_medocs_quantities, names_medocs, quantities_medocs
        )
        if self.switch_speaker.value:
            self.page.run_thread(
                self.__speack_with_args,
                self.montant_chiffre.value,
                "francs" if self.devises.value == "FC" else "dollars",
            )
        if self.page.overlay:
            self.page.overlay.clear()
        self.page.overlay.append(
            SnackBar(Text("La vente a été enregistrée avec succès"), open=True)
        )
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page in finaliser facture: {e}")

        self.imprimer_facture(num_facture)

    def imprimer_facture(self, num_facture):
        liste_medocs_facture = [
            ["N°", "QTE", "FORME", "PRODUIT", "PRIX UNITAIRE", "PRIX TOTAL"]
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
                prix_total=str(self.totaux.value),
                reduction=str(self.reduction_accordee.value) + " " + self.devises.value,
                charges_connexes=str(self.charges_connexes.value)
                + " "
                + self.devises.value,
                date=self.date_field.value.strip()+datetime.datetime.now().strftime(" %H:%M:%S"),
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

    def handler_keyboard_key(self, e: KeyboardEvent):
        try:
            if self.page:
                match e.key:
                    case "Escape":
                        self.__reinitialiser_entree(None)
                    case "Enter":
                        self.add_medoce_panier(None)
        except Exception as e:
            print(e)


class Accueil(Container):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.taux_dollar = CupertinoTextField(
            value=str(self.page.client_storage.get("taux") or "2900"),
            width=100,
            keyboard_type=KeyboardType.NUMBER,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
        )
        self.__principal_view = PrincipalView(
            self.page,
            draft_handler=self.__add_draft,
            taux_dollar=self.taux_dollar.value,
        )
        self.__produits_view = ProduitsView(
            self.page,
            self.__add_new_product,
            self.__change_view_to_entree_stock,
        )
        self.__entree_stock_view = EntreeStockView(self.page)
        self.__clients_view = Column()
        self.current_view = Container(
            content=self.__principal_view, expand=True, expand_loose=True
        )
        self.list_medocs_draft = ListView(
            auto_scroll=True,
            controls=self.init_drafts(),
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
                    width=self.page.width * 0.20,
                    content=self._menu(),
                    clip_behavior=ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
                    border_radius=border_radius.only(top_right=15),
                ),
                self.current_view,
            ],
        )
        # self.__principal_view.init_drafts()
        self.init_drafts()

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
                                disabled=True,
                            ),
                            CustomElevatedButton(
                                text="Tableau de bord",
                                icon=Icons.BAR_CHART,
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
        try:
            self.current_view.content = self.__entree_stock_view
            self.page.on_keyboard_event = self.__entree_stock_view.handler_keyboard_key
            try:
                self.current_view.update()
            except Exception as e:
                print(f"Error updating current view: {e}")
        except Exception as e:
            print(e)

    def __change_view(self, e: ControlEvent):
        try:
            match e.control.text:
                case "Accueil":
                    self.current_view.content = self.__principal_view
                    self.page.on_keyboard_event = (
                        self.__principal_view.handler_keyboard_key
                    )
                    self.__principal_view.list_all_medocs_db = db.get_all_medocs_list()
                case "Produits":
                    self.current_view.content = self.__produits_view
                    self.__produits_view.all_medocs_for_preview = (
                        db.get_medocs_for_list_preview()
                    )
                    self.page.on_keyboard_event = None
                case "Ventes":
                    self.current_view.content = VenteView(
                        self.page,
                        self.__add_new_product,
                        self.__change_view_to_entree_stock,
                    )
                    self.page.on_keyboard_event = None
                case "Clients":
                    self.current_view.content = self.__clients_view
                    self.page.on_keyboard_event = None
                case "Tableau de bord":
                    self.current_view.content = TableauBordView(self.page)
                    self.page.on_keyboard_event = None
            try:
                self.current_view.update()
            except Exception as e:
                print(f"Error updating current view: {e}")
        except Exception as e:
            print(e)

    def __change_taux_dollar(self, e):
        if self.taux_dollar.value:
            self.page.client_storage.set("taux", float(self.taux_dollar.value))
            self.__principal_view.handler_change_taux(float(self.taux_dollar.value))
            if self.page.overlay:
                self.page.overlay.clear()
            self.page.overlay.append(
                SnackBar(
                    content=Text(
                        f"Le taux du dollar a été modifié : 1$ = {self.taux_dollar.value} FC"
                    ),
                    open=True,
                    show_close_icon=True,
                )
            )
            try:
                self.page.update()
            except Exception as e:
                print(f"Error updating page: {e}")

    def __select_date(self, e: ControlEvent):
        self.current_date = e.control.value
        self.date_field.value = str(e.control.value.strftime("%d-%m-%Y"))
        try:
            self.date_field.update()
        except Exception as e:
            print(f"Error updating date field: {e}")

    def __add_new_product(self, e):
        self.page.on_keyboard_event = None
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
            value="", read_only=True, height=40, multiline=True
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
            on_click=self.__add_medoc_to_db,
            height=40,
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
                    height=40,
                ),
                self.button_ajouter,
            ],
        )

        self.page.open(self.dialog)
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def __pick_file_db(self, result: FilePickerResultEvent):
        try:
            self.db_file_picked.value = result.files[0].name
            try:
                self.db_file_picked.update()
            except Exception as e:
                print(f"Error updating db_file_picked: {e}")
            self.path_csv = result.files[0].path
        except Exception as e:
            print(f"Error picking file: {e}")
        finally:
            try:
                self.page.update()
            except Exception as e:
                print(f"Error updating page: {e}")

    def __add_draft(self, list_draft, nom_client, date):
        self.list_medocs_draft.controls.append(
            CustomDraftButton(
                self.page,
                list_draft,
                nom_client if nom_client else "",
                date,
                self.__delete_draft,
                self.__load_draft,
            )
        )
        try:
            self.list_medocs_draft.update()
        except Exception as e:
            print(f"Error updating list_medocs_draft: {e}")

    def __verifier_produit(self, e):
        if self.nom.value:
            if db.is_medoc_exists(self.nom.value.upper()):
                self.button_ajouter.disabled = True
                self.button_ajouter.bgcolor = "#B4B4B4"
                self.nom.error_text = "Ce produit existe déjà"
                try:
                    self.nom.update()
                    self.button_ajouter.update()
                except Exception as e:
                    print(f"Error updating fields: {e}")
            else:
                self.nom.error_text = ""
                self.button_ajouter.disabled = False
                self.button_ajouter.bgcolor = "blue"
                try:
                    self.button_ajouter.update()
                    self.nom.update()
                except Exception as e:
                    print(f"Error updating fields: {e}")

    def __add_medoc_to_db(self, e):
        if self.db_file_picked.value:
            try:
                db.import_csv_to_db(self.path_csv)
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(
                        Text("Les produits ont été ajoutés avec succès"), open=True
                    )
                )
                try:
                    self.page.update()
                except Exception as e:
                    print(f"Error updating page: {e}")
            except Exception as e:
                print(f"Error importing CSV: {e}")
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Une erreur est survenue !"), open=True)
                )
                try:
                    self.page.update()
                except Exception as e:
                    print(f"Error updating page: {e}")
            finally:
                try:
                    self.page.close(self.dialog)
                    self.page.update()
                except Exception as e:
                    print(f"Error closing dialog or updating page: {e}")
                return
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
                db.add_medoc(
                    (
                        self.nom.value.upper(),
                        self.forme.value.upper(),
                        datetime.datetime.now(),
                        datetime.datetime.strptime(
                            self.date_field.value, "%d-%m-%Y"
                        ).date(),
                        float(self.prix_achat.value),
                        float(self.prix_vente.value),
                    )
                )

            except Exception as e:
                print(f"Error adding medoc: {e}")
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Erreur lors de l'ajout du produit"), open=True)
                )
            else:
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Le produit a été ajouté avec succès"), open=True)
                )
            try:
                self.__principal_view.list_all_medocs_db = db.get_all_medocs_list()
                self.__principal_view.reinitialiser_entree_produit_new()
            except Exception as e:
                print(f"Error updating autocompletion after adding new medoc")
        try:
            self.page.close(self.dialog)
            self.page.update()            
        except Exception as e:
            print(f"Error closing dialog or updating page: {e}")

    def __renitialiser_produit(self, e):
        self.nom.value = ""
        self.forme.value = ""
        self.prix_achat.value = "0"
        self.prix_vente.value = "0"
        self.date_field.value = str(self.current_date.strftime("%d-%m-%Y"))
        self.db_file_picked.value = " "
        try:
            self.nom.update()
            self.forme.update()
            self.prix_achat.update()
            self.prix_vente.update()
            self.date_field.update()
            self.db_file_picked.update()
        except Exception as e:
            print(f"Error updating fields: {e}")

    def __delete_draft(self, e):
        self.list_medocs_draft.controls.remove(e)
        try:
            self.list_medocs_draft.update()
        except Exception as e:
            print(f"Error updating list_medocs_draft: {e}")
        nom_client = "" if e.nom_client == "" else e.nom_client
        date = e.date
        list_medocs_drafts = []
        for medoc in e.list_medicaments:
            list_medocs_drafts.append(
                (
                    medoc.nom.value,
                    medoc.quantite.value,
                    medoc.forme.value,
                    medoc.prix_unitaire.value,
                    medoc.prix_total.value,
                    nom_client,
                    date,
                    medoc.devise.value,
                )
            )
        drafts = init_load_drafts()
        try:
            drafts.remove(list_medocs_drafts)
            save_drafts(drafts)
        except Exception as e:
            print(e)

    def __load_draft(self, e):
        if self.current_view.content != self.__principal_view:
            return
        try:
            self.__principal_view.load_draft(e.list_medicaments, e.nom_client)
        except Exception as e:
            print(f"Error loading draft: {e}")
        # self.__delete_draft(e)

    def init_drafts(self):
        drafts = init_load_drafts()
        all_drafts = []
        if drafts:
            for draft_l in drafts:
                list_drafts = []
                client_name = " "
                date = " "
                for draft in draft_l:
                    client_name = draft[5]
                    date = draft[6]
                    list_drafts.append(
                        Medicament(
                            nom=draft[0],
                            quantite=draft[1],
                            forme=draft[2],
                            prix_unitaire=draft[3],
                            prix_total=draft[4],
                            medoc_delete=self.__principal_view._delete_medoc,
                            calcul_totaux=self.__principal_view._calcul_totaux,
                            devise_initiale=draft[7],
                        )
                    )
                all_drafts.append(
                    CustomDraftButton(
                        self.page,
                        list_drafts,
                        client_name if client_name else "",
                        date,
                        self.__delete_draft,
                        self.__load_draft,
                    )
                )
        try:
            self.list_medocs_draft.update()
        except Exception as e:
            print(f"Error updating list_medocs_draft: {e}")
        return all_drafts

        # self._calcul_totaux()


class VenteView(Column):
    def __init__(
        self, page: Page, handler_entree_produit=None, handler_entree_stock=None
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
                    on_click=lambda e: self.page.run_thread(self.__restore_search_bar),
                )
            ],
            on_blur=lambda e: self.page.run_thread(self.__search_invoice),
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
                DataColumn(label=Text("Devise", weight=FontWeight.BOLD, color="white")),
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
                                    height=40,
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
                                    height=40,
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
                                    height=40,
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
                    scroll=ScrollMode.ALWAYS,
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
                        height=40,
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
                        height=40,
                    ),
                ],
            ),
        ]

    def __restore_search_bar(self):
        self.search_bar.value = ""
        try:
            self.search_bar.update()
        except Exception as e:
            print(f"Error updating search bar: {e}")
        self.data_table.rows = list(self.__invoices())
        try:
            self.data_table.update()
        except Exception as e:
            print(f"Error updating data table: {e}")

    def __search_invoice(self):
        try:
            invoices_found = db.get_all_mouvement_facture_by_client_name(
                self.search_bar.value.upper()
            )
            if invoices_found:
                self.data_table.rows = list(self.__invoices_searched(invoices_found))
                try:
                    self.data_table.update()
                except Exception as e:
                    print(f"Error updating data table: {e}")
            else:
                if self.page.overlay:
                    self.page.overlay.clear()
                self.page.overlay.append(
                    SnackBar(Text("Aucune facture trouvée"), open=True)
                )
            self.page.update()
        except Exception as e:
            print(f"Error searching invoice: {e}")

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
                    DataCell(Text(invoice[9])),
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
        #print(f"Start index : {start_index}")
        end_index = start_index + self.items_per_page
        #print(f"End index : {end_index}")
        invoices = db.get_all_mouvement_facture()#[start_index:end_index]

        unique_invoices = {}
        for invoice in invoices:
            if invoice[6] not in unique_invoices:
                unique_invoices[invoice[6]] = {"invoice": invoice, "total": 0}
            unique_invoices[invoice[6]]["total"] += float(invoice[5])
        # unique_invoices = unique_invoices[start_index:end_index]
        for invoice_data in unique_invoices.values():
            invoice = invoice_data["invoice"]
            total = invoice_data["total"]
            total = round(total, 3)
            yield DataRow(
                cells=[
                    DataCell(Text(invoice[6])),
                    DataCell(Text(invoice[7])),
                    DataCell(Text(invoice[8])),
                    DataCell(Text(str(total))),
                    DataCell(Text(invoice[9])),
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
        try:
            self.data_table.update()
        except Exception as e:
            print(f"Error updating data table: {e}")
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def __print_invoice(self, invoice_id):
        # Implement the logic to print the invoice using the invoice_id
        list_medocs = db.get_all_mouvement_facture_by_id_facture(invoice_id)
        nom_client = list_medocs[0][7]
        date = list_medocs[0][8]
        montant_total = 0
        for medoc in list_medocs:
            montant_total += float(medoc[5])
        montant_total = round(montant_total, 3)
        liste_medocs_facture = [
            ["N°", "QTE", "FORME", "PRODUIT", "PRIX UNITAIRE", "PRIX TOTAL"]
        ]
        for index, medoc in enumerate(list_medocs, start=1):
            liste_medocs_facture.append(
                [
                    str(index),
                    medoc[1],
                    medoc[2],
                    medoc[3],
                    medoc[4],
                    medoc[5],
                ]
            )
        totaux = montant_total - list_medocs[0][10] + list_medocs[0][11]
        totaux = round(totaux, 3)
        facture_thread = Thread(
            target=generer_facture,
            kwargs=dict(
                list_medicaments=liste_medocs_facture,
                prix_total=str(montant_total) + list_medocs[0][9],
                reduction=str(list_medocs[0][10]) + " " + list_medocs[0][9],
                charges_connexes=str(list_medocs[0][11]) + " " + list_medocs[0][9],
                date=date,
                nom_client=nom_client,
                num_facture=invoice_id,
                bar_code="F-"
                + str(invoice_id)
                + "-"
                + str(datetime.datetime.now().year),
                montant_final=str(totaux) + " " + list_medocs[0][9],
                montant_en_lettres=number_to_words(round(float(montant_total), 3))
                + " "
                + list_medocs[0][9],
            ),
        )
        facture_thread.start()


class TableauBordView(Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.controls = [
            Container(
                bgcolor="black",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Text("Tableau de bord", size=20, weight="bold", color="white"),
                alignment=alignment.center_left,
            ),
            Container(
                expand=True,
                padding=padding.symmetric(horizontal=20, vertical=10),
                alignment=alignment.center_left,
                content=Column(
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    controls=[
                        Row(
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                CardTableauBord(
                                    self.page,
                                    title="MEDICAMENTS ENREGISTRES",
                                    quantite=self.__medocs_enreigistrer(),
                                ),
                                CardTableauBord(
                                    self.page,
                                    title="TOTAL VENDU",
                                    quantite=self.__total_vendu(),
                                    bgcolor="blue",
                                    title_color="white",
                                    divider_color="#88AEFF",
                                    qte_color="#ECECEC",
                                ),
                                CardTableauBord(
                                    self.page,
                                    title="TOTAL VENDU AUJOURD'HUI",
                                    quantite=self.__total_vendu_aujourdhui(),
                                    bgcolor="blue",
                                    title_color="white",
                                    divider_color="#88AEFF",
                                    qte_color="#ECECEC",
                                ),
                            ],
                        ),
                        Row(
                            alignment=MainAxisAlignment.SPACE_AROUND,
                            controls=[
                                CardTableauBord(
                                    self.page,
                                    title="DERNIERE VENTE",
                                    quantite=self.__total_derniere_vente(),
                                ),
                                CardTableauBord(
                                    self.page,
                                    title="LE PLUS VENDU",
                                    quantite=self.__medoc_le_plus_vendu(),
                                    bgcolor="#EBEBEB",
                                    qte_size=14,
                                ),
                                CardTableauBord(
                                    self.page,
                                    title="TOP CLIENT",
                                    quantite=self.__client_top(),
                                    qte_size=12,
                                    qte_color="green",
                                    badge=Badge(text="🥇"),
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        ]

    def __medocs_enreigistrer(self):
        return len(db.get_all_medocs_list())

    def __total_vendu(self):
        total_vendu = 0
        for invoice in db.get_all_mouvement_facture():
            total_vendu += float(invoice[5])
        return str(round(total_vendu, 3)) + " FC"

    def __total_vendu_aujourdhui(self):
        total_vendu_aujourdhui = 0
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        for invoice in db.get_all_mouvement_facture():
            if invoice[8].startswith(today):
                total_vendu_aujourdhui += float(invoice[5])
        return str(round(total_vendu_aujourdhui, 3)) + " FC"

    def __total_derniere_vente(self):
        total_derniere_vente = 0
        devise = "FC"
        all_invoices = db.get_all_mouvement_facture()
        if all_invoices:
            last_invoice_id = all_invoices[-1][6]
            for invoice in all_invoices:
                if invoice[6] == last_invoice_id:
                    total_derniere_vente += float(invoice[5])
                    devise = invoice[9]
        return str(round(total_derniere_vente, 3)) + " " + devise

    def __medoc_le_plus_vendu(self):
        medoc_sales = {}
        for invoice in db.get_all_mouvement_facture():
            medoc_name = invoice[3]
            quantite = int(invoice[1])
            if medoc_name in medoc_sales:
                medoc_sales[medoc_name] += quantite
            else:
                medoc_sales[medoc_name] = quantite
        if medoc_sales:
            medoc_le_plus_vendu = max(medoc_sales, key=medoc_sales.get)
            return f"{medoc_le_plus_vendu}"
        return "Aucun médicament vendu"

    def __client_top(self):
        clients = {}
        for invoice in db.get_all_mouvement_facture():
            client_name = invoice[7]
            total_amount = float(invoice[5])
            if client_name in clients:
                clients[client_name] += total_amount
            else:
                clients[client_name] = total_amount
        if clients:
            top_client = max(clients, key=clients.get)
            return f"{top_client} ({clients[top_client]} FC)"
        return "Aucun client"


class CardTableauBord(Container):
    def __init__(
        self,
        page: Page,
        bgcolor: str = "white",
        title: str = "",
        quantite: str | int | float = 0,
        title_color="black",
        divider_color="blue",
        qte_color="#7E7E7E",
        qte_size=18,
        badge=None,
    ):
        super().__init__(self)
        self.page = page
        self.height = 100
        self.width = 300
        self.badge = badge
        self.bgcolor = bgcolor
        self.shadow = BoxShadow(blur_radius=2, color="#DADADA")
        self.padding = padding.all(10)
        self.border_radius = border_radius.all(15)
        self.content = Column(
            alignment=MainAxisAlignment.CENTER,
            spacing=5,
            controls=[
                Text(
                    value=title,
                    size=18,
                    color=title_color,
                    weight="bold",
                ),
                Divider(thickness=2, color=divider_color),
                Text(
                    value=quantite,
                    size=qte_size,
                    color=qte_color,
                ),
            ],
        )


def main(page: Page):
    def on_route_change(route: RouteChangeEvent):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    LoginView(page),
                ],
                padding=padding.all(0),
            )
        )
        if page.route == "/home":
            page.views.append(
                View(
                    "/home",
                    [
                        Accueil(page),
                    ],
                    padding=padding.all(0),
                )
            )
        try:
            page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def on_view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    def yes_click(e):
        db.close()
        page.window.destroy()
        # page.update()

    def no_click(e):
        page.close(confirm_dialog)

    page.padding = padding.all(0)
    page.title = "PHARMACIE SHEKINA"
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

    confirm_dialog = AlertDialog(
        modal=True,
        title=Text("Veuillez confirmer"),
        content=Text("Voulez-vous quitter ?"),
        actions=[
            ElevatedButton("Oui, quitter", on_click=yes_click),
            OutlinedButton("Non, annuler", on_click=no_click),
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.go(page.route)


app(
    main,
    assets_dir=str(Path(__file__).parent.resolve()).replace("\\", "/") + "/assets",
)
