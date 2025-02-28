import datetime
from db.db_utils import DBUtils
from components.CustomTextField import CustomTextField
from flet import (
    Column,
    CrossAxisAlignment,
    DataTable,
    DataColumn,
    DataRow,
    DataCell,
    Text,
    Button,
    MainAxisAlignment,
    Row,
    SearchBar,
    Icon,
    Icons,
    AlertDialog,
    InputFilter,
    Page,
    ControlEvent,
    SnackBar,
    RoundedRectangleBorder,
    BorderSide,
    ButtonStyle,
    ScrollMode,
    DatePicker,
    FontWeight,
    Container,
    padding,
    border_radius,
    IconButton,
    ControlState,
)


class ProduitsView(Column):

    def __init__(
        self,
        page: Page,
        handler_entree_produit=None,
        handler_entree_stock=None,
        db: DBUtils = None,
    ):
        super().__init__()
        self.page = page
        self.handler_entree_produit = handler_entree_produit
        self.handler_entree_stock = handler_entree_stock
        self.current_page = 0
        self.expand = True
        self.db = db
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.items_per_page = 50
        self.all_medocs_for_preview = self.db.get_medocs_for_list_preview()
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
            products_founds = self.db.get_medocs_for_list_preview_by_containing_name(
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
                quantite = self.db.get_medoc_quantity_by_id(
                    self.db.get_medoc_id_by_name(medoc[0])
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
                quantite = self.db.get_medoc_quantity_by_id(
                    self.db.get_medoc_id_by_name(medoc[0])
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
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*|-\d*)$"),
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
        self.date_field.value = str(e.control.value.strftime("%Y-%m-%d"))
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
                self.db.update_medoc_to_accounts_produit_by_medoc_name(
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
                medoc_id = self.db.get_medoc_id_by_name(self.nom.value)
                self.db.update_medoc_quantity_by_id(
                    medoc_id, int(self.stock_quantite.value)
                )
                self.db.update_medoc_designation_by_id(medoc_id, self.forme.value)
                self.all_medocs_for_preview = self.db.get_medocs_for_list_preview()
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
                self.db.delete_medoc(self.nom.value)
                self.all_medocs_for_preview = self.db.get_medocs_for_list_preview()
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
