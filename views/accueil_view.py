import datetime
from db.db_utils import DBUtils
from pathlib import Path
from utils.drafts_utils import init_load_drafts, save_drafts

from views.dashboard_view import TableauBordView
from views.entree_stock_view import EntreeStockView
from views.produits_view import ProduitsView
from views.principal_view import PrincipalView
from views.notifications_view import NotificationsView
from views.vente_view import VenteView

from models.medicament import Medicament
from components.CustomDraftButton import CustomDraftButton
from components.CustomTextField import CustomTextField
from components.CustomElevatedButton import CustomElevatedButton


from flet import (
    Page,
    Container,
    CupertinoTextField,
    KeyboardType,
    InputFilter,
    Icons,
    Badge,
    Column,
    ListView,
    AlertDialog,
    Button,
    ButtonStyle,
    RoundedRectangleBorder,
    DatePicker,
    FilePicker,
    FilePickerResultEvent,
    SnackBar,
    Text,
    Row,
    IconButton,
    Icon,
    PopupMenuButton,
    PopupMenuItem,
    alignment,
    padding,
    border_radius,
    Colors,
    BoxShadow,
    ClipBehavior,
    ControlEvent,
    ScrollMode,
    Image,
    TextAlign,
    FontWeight,
    MainAxisAlignment,
    CrossAxisAlignment,
    Divider,
)


class AccueilView(Container):
    def __init__(self, page: Page, db: DBUtils):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.taux_dollar = CupertinoTextField(
            value=str(self.page.client_storage.get("taux") or "2900"),
            width=100,
            keyboard_type=KeyboardType.NUMBER,
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
        )
        self.notifications_button = CustomElevatedButton(
            text="Notifications",
            icon=Icons.NOTIFICATIONS,
            on_click=self.__change_view,
            badge=Badge(
                text="0",
                alignment=alignment.top_center,
                bgcolor="red",
                text_color="white",
            ),
        )
        self.__principal_view = PrincipalView(
            self.page,
            draft_handler=self.__add_draft,
            taux_dollar=self.taux_dollar.value,
            db=db,
        )
        self.__produits_view = ProduitsView(
            self.page,
            self.__add_new_product,
            self.__change_view_to_entree_stock,
            db,
        )
        self.__entree_stock_view = EntreeStockView(self.page, db)
        self.__clients_view = Column()
        self.current_view = Container(
            content=self.__principal_view, expand=True, expand_loose=True
        )
        self.__notifications_views = NotificationsView(
            self.page, self.notifications_button, db
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
                                src=str(Path(__file__).parent.parent.resolve()).replace(
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
                            self.notifications_button,
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
                    self.__principal_view.list_all_medocs_db = (
                        self.db.get_all_medocs_list()
                    )
                case "Produits":
                    self.current_view.content = self.__produits_view
                    self.__produits_view.all_medocs_for_preview = (
                        self.db.get_medocs_for_list_preview()
                    )
                    self.page.on_keyboard_event = None
                case "Ventes":
                    self.current_view.content = VenteView(
                        self.page,
                        self.__add_new_product,
                        self.__change_view_to_entree_stock,
                        self.db,
                    )
                    self.page.on_keyboard_event = None
                case "Clients":
                    self.current_view.content = self.__clients_view
                    self.page.on_keyboard_event = None
                case "Tableau de bord":
                    self.current_view.content = TableauBordView(self.page, self.db)
                    self.page.on_keyboard_event = None
                case "Notifications":
                    self.current_view.content = self.__notifications_views
                    self.__notifications_views.refresh_notifications()
                    self.page.on_keyboard_event = None
            try:
                self.current_view.update()
            except Exception as e:
                print(f"Error updating current view: {e}")
        except Exception as e:
            print(e, " : on changing view")

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
        self.date_field.value = str(e.control.value.strftime("%Y-%m-%d"))
        self.__verifier_expiration_produit(None)
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
        self.current_date = datetime.datetime.now() + datetime.timedelta(days=30)
        self.date_field = CustomTextField(
            label="Date d'expiration",
            read_only=True,
            height=60,
            value=str(self.current_date.strftime("%Y-%m-%d")),
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
            on_dismiss=self.__dialog_dismiss,
        )

        self.page.open(self.dialog)
        try:
            self.page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def __dialog_dismiss(self, e):
        if self.current_view.content != self.__principal_view:
            return
        try:
            self.page.on_keyboard_event = self.__principal_view.handler_keyboard_key
        except Exception as e:
            print(f"Error setting on_keyboard_event: {e}")

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
            if self.db.is_medoc_exists(self.nom.value.upper()):
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

    def __verifier_expiration_produit(self, e):
        if self.date_field.value:
            if (
                datetime.datetime.strptime(self.date_field.value, "%Y-%m-%d").date()
                < datetime.datetime.now().date()
            ):
                self.button_ajouter.disabled = True
                self.button_ajouter.bgcolor = "#B4B4B4"
                self.date_field.error_text = "Le produit est déjà expiré"
                try:
                    self.date_field.update()
                    self.button_ajouter.update()
                except Exception as e:
                    print(f"Error updating fields: {e}")
            else:
                self.date_field.error_text = ""
                self.button_ajouter.disabled = False
                self.button_ajouter.bgcolor = "blue"
                try:
                    self.button_ajouter.update()
                    self.date_field.update()
                except Exception as e:
                    print(f"Error updating fields: {e}")

    def __add_medoc_to_db(self, e):
        if self.db_file_picked.value:
            try:
                self.db.import_csv_to_db(self.path_csv)
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
                    if self.page.overlay:
                        self.page.overlay.clear()
                    self.page.on_keyboard_event = (
                        self.__principal_view.handler_keyboard_key
                    )
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
                self.db.add_medoc(
                    (
                        self.nom.value.upper(),
                        self.forme.value.upper(),
                        datetime.datetime.now(),
                        datetime.datetime.strptime(
                            self.date_field.value, "%Y-%m-%d"
                        ).date(),
                        float(self.prix_achat.value),
                        float(self.prix_vente.value),
                    )
                )

            except Exception as e:
                print(f"Error adding medoc: {e}")
                self.page.overlay.append(
                    SnackBar(Text("Erreur lors de l'ajout du produit"), open=True)
                )
            else:
                self.page.overlay.append(
                    SnackBar(Text("Le produit a été ajouté avec succès"), open=True)
                )
            try:
                self.__principal_view.list_all_medocs_db = self.db.get_all_medocs_list()
                self.__principal_view.reinitialiser_entree_produit_new()
            except Exception as e:
                print(f"Error updating autocompletion after adding new medoc")
        try:
            self.page.close(self.dialog)
            self.page.update()
            if self.page.overlay:
                self.page.overlay.clear
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
            print(e, " : in Accueil - __delete_draft")

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
        # try:
        #     self.list_medocs_draft.update()
        # except Exception as e:
        #     print(f"Error updating list_medocs_draft: {e}")
        return all_drafts

        # self._calcul_totaux()
