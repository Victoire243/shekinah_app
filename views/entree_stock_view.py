from components.CustomTextField import CustomTextField
from models.medicament_entree import MedicamentEntree
from db.db_utils import DBUtils
from flet import (
    Row,
    Column,
    Container,
    Text,
    Icon,
    IconButton,
    Button,
    RoundedRectangleBorder,
    MainAxisAlignment,
    FontWeight,
    ScrollMode,
    padding,
    border_radius,
    InputFilter,
    NumbersOnlyInputFilter,
    AutoComplete,
    AutoCompleteSuggestion,
    AutoCompleteSelectEvent,
    SnackBar,
    MainAxisAlignment,
    CrossAxisAlignment,
    ResponsiveRow,
    ListView,
    KeyboardEvent,
    Icons,
    ButtonStyle,
    Page,
)


class EntreeStockView(Column):
    def __init__(self, page: Page, db: DBUtils):
        super().__init__()
        self.page = page
        self.db = db
        self.spacing = 0
        self.list_all_medocs_db = self.db.get_all_medocs_list()
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
        medoc = self.db.get_medocs_by_name(e.selection.key)
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
        ) and self.db.is_medoc_exists(
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
            medoc_quantite = self.db.get_medoc_quantity_by_name(medoc.nom.value)
            try:
                names_medocs.append(medoc.nom.value)
                quantities_medocs.append(
                    int(float(medoc_quantite or 0) + float(medoc.quantite.value or 0))
                )
                self.db.add_new_medoc_to_accounts_mouvement_in(
                    designation=medoc.forme.value or "",
                    qte=int(medoc.quantite.value),
                    pu=float(medoc.prix_unitaire_vente.value),
                    produit_id=self.db.get_medoc_id_by_name(medoc.nom.value),
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
            self.db.update_medocs_quantities, names_medocs, quantities_medocs
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
