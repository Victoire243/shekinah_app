import datetime
from threading import Thread
from db.db_utils import DBUtils
from utils.impression_facture import generer_facture
from utils.nombre_to_chiffre import number_to_words
from flet import (
    Page,
    Column,
    CrossAxisAlignment,
    DataTable,
    DataColumn,
    Text,
    DataRow,
    DataCell,
    IconButton,
    Icons,
    Button,
    ButtonStyle,
    MainAxisAlignment,
    SearchBar,
    BorderSide,
    RoundedRectangleBorder,
    SnackBar,
    ScrollMode,
    FontWeight,
    Icon,
    Container,
    Row,
    border_radius,
    ControlState,
    padding,
)


class VenteView(Column):

    def __init__(
        self,
        page: Page,
        handler_entree_produit=None,
        handler_entree_stock=None,
        db: DBUtils = None,
    ):
        super().__init__()
        self.page = page
        self.db = db
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
            invoices_found = self.db.get_all_mouvement_facture_by_client_name(
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
        # print(f"Start index : {start_index}")
        end_index = start_index + self.items_per_page
        # print(f"End index : {end_index}")
        invoices = self.db.get_all_mouvement_facture()  # [start_index:end_index]

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
        list_medocs = self.db.get_all_mouvement_facture_by_id_facture(invoice_id)
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
