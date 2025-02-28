import datetime
from threading import Thread
from utils.speaker import Speaker
from db.db_utils import DBUtils
from components.CustomTextField import CustomTextField
from utils.impression_facture import generer_facture
from utils.nombre_to_chiffre import number_to_words
from utils.drafts_utils import init_load_drafts, save_drafts
from models.medicament import Medicament
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
    alignment,
    padding,
    border_radius,
    InputFilter,
    NumbersOnlyInputFilter,
    AutoComplete,
    AutoCompleteSuggestion,
    AutoCompleteSelectEvent,
    DatePicker,
    ControlEvent,
    Dropdown,
    dropdown,
    SnackBar,
    MainAxisAlignment,
    CrossAxisAlignment,
    ResponsiveRow,
    ListView,
    KeyboardEvent,
    Icons,
    ButtonStyle,
    Page,
    Switch,
)


class PrincipalView(Column):

    def __init__(
        self, page: Page, draft_handler=None, taux_dollar=None, db: DBUtils = None
    ):
        super().__init__()
        self.current_date = datetime.datetime.now()
        self.page = page
        self.db = db
        self.taux_dollar = taux_dollar
        self.spacing = 0
        self.list_all_medocs_db = self.db.get_all_medocs_list()
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
            and self.db.is_medoc_exists(
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
            label="Forme",
            col=2,
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
        medoc = self.db.get_medocs_by_name(e.selection.key)
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

        num_facture = self.db.get_last_facture_id() + 1
        names_medocs = []
        quantities_medocs = []
        for medoc in (
            self.list_medocs_panier.controls if self.list_medocs_panier.controls else []
        ):

            medoc_quantite = self.db.get_medoc_quantity_by_name(medoc.nom.value)
            try:
                names_medocs.append(medoc.nom.value)
                quantities_medocs.append(
                    int(float(medoc_quantite or 0) - float(medoc.quantite.value or 0))
                )
                self.db.add_to_accounts_mouvement_facture(
                    quantite=int(medoc.quantite.value) or 0,
                    forme=medoc.forme.value or " ",
                    produit=medoc.nom.value,
                    prix_unitaire=round(float(medoc.prix_unitaire.value), 3) or 0,
                    prix_total=round(float(medoc.prix_total.value), 3) or 0,
                    id_facture=num_facture,
                    nom_client=self.nom_client.value,
                    date=self.date_field.value
                    + datetime.datetime.now().strftime(" %H:%M:%S"),
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
            self.db.update_medocs_quantities, names_medocs, quantities_medocs
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
                date=self.date_field.value.strip()
                + datetime.datetime.now().strftime(" %H:%M:%S"),
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
