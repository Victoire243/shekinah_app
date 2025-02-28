import datetime
from db.db_utils import DBUtils
from flet import (
    Page,
    Container,
    padding,
    alignment,
    CrossAxisAlignment,
    Text,
    Column,
    MainAxisAlignment,
    Row,
    Badge,
    border_radius,
    Divider,
    BoxShadow,
)


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


class TableauBordView(Column):
    def __init__(self, page: Page, db: DBUtils):
        super().__init__()
        self.page = page
        self.expand = True
        self.db = db
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.invoices = self.db.get_all_mouvement_facture()
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
        return len(self.db.get_all_medocs_list())

    def __total_vendu(self):
        total_vendu_fc = 0
        total_vendu_usd = 0
        for invoice in self.invoices:
            total_vendu_fc += float(invoice[5]) if invoice[9] == "FC" else 0
            total_vendu_usd += float(invoice[5]) if invoice[9] == "$" else 0
        return f"{round(total_vendu_fc, 3)} FC & {round(total_vendu_usd, 3)} $"

    def __total_vendu_aujourdhui(self):
        total_vendu_aujourdhui = 0
        today = datetime.datetime.now().strftime("%d-%m-%Y")
        for invoice in self.invoices:
            if invoice[8].startswith(today):
                total_vendu_aujourdhui += float(invoice[5])
        return str(round(total_vendu_aujourdhui, 3)) + " FC"

    def __total_derniere_vente(self):
        total_derniere_vente = 0
        devise = "FC"
        if self.invoices:
            last_invoice_id = self.invoices[-1][6]
            for invoice in self.invoices:
                if invoice[6] == last_invoice_id:
                    total_derniere_vente += float(invoice[5])
                    devise = invoice[9]
        return str(round(total_derniere_vente, 3)) + " " + devise

    def __medoc_le_plus_vendu(self):
        return self.db.get_medoc_plus_vendu()

    def __client_top(self):
        return self.db.get_top_client()
