from db.db_utils import DBUtils
import datetime
from components.CustomElevatedButton import CustomElevatedButton
from flet import (
    Page,
    Column,
    Container,
    Text,
    MainAxisAlignment,
    CrossAxisAlignment,
    ScrollMode,
    ListTile,
    ExpansionTile,
    TileAffinity,
    padding,
    alignment,
    border_radius,
    BoxShadow,
    Badge,
    FontWeight,
    RoundedRectangleBorder,
    ResponsiveRow,
    TextStyle,
    border,
)


class NotificationsView(Column):
    def __init__(
        self, page: Page, notifications_button: CustomElevatedButton, db: DBUtils
    ):
        super().__init__()
        self.db = db
        self.page = page
        self.notifications_button = notifications_button
        self.expand = True
        self.horizontal_alignment = CrossAxisAlignment.STRETCH
        self.medocs_names_qte_expration = (
            self.db.get_all_medocs_names_quantity_expiration_date()
        )
        self.body = Container(
            expand=True,
            padding=padding.symmetric(horizontal=20, vertical=10),
            alignment=alignment.top_center,
        )
        self.controls = [
            Container(
                bgcolor="black",
                height=110,
                border_radius=border_radius.only(top_left=15, top_right=15),
                padding=padding.symmetric(horizontal=20, vertical=10),
                content=Text("Notifications", size=20, weight="bold", color="white"),
                alignment=alignment.center_left,
            ),
            self.body,
        ]
        self.page.run_thread(self.__expirations)

    def refresh_notifications(self):
        self.medocs_names_qte_expration = (
            self.db.get_all_medocs_names_quantity_expiration_date()
        )
        self.__expirations()

    def __expirations(self):
        self.medocs_expire_in_one_week = []
        self.medocs_expire_in_one_month = []
        self.medocs_expire_in_two_month = []
        self.medocs_expire_in_tree_month = []
        self.medocs_expired = []
        self.medocs_qte_inf_50 = []
        self.medocs_qte_inf_0 = []
        for medoc in self.medocs_names_qte_expration:
            if (
                datetime.datetime.strptime(medoc[2], "%Y-%m-%d").date()
                < datetime.datetime.now().date()
            ):
                self.medocs_expired.append(medoc)
            elif datetime.datetime.strptime(
                medoc[2], "%Y-%m-%d"
            ).date() < datetime.datetime.now().date() + datetime.timedelta(days=7):
                self.medocs_expire_in_one_week.append(medoc)
            elif datetime.datetime.strptime(
                medoc[2], "%Y-%m-%d"
            ).date() < datetime.datetime.now().date() + datetime.timedelta(days=30):
                self.medocs_expire_in_one_month.append(medoc)
            elif datetime.datetime.strptime(
                medoc[2], "%Y-%m-%d"
            ).date() < datetime.datetime.now().date() + datetime.timedelta(days=60):
                self.medocs_expire_in_two_month.append(medoc)
            elif datetime.datetime.strptime(
                medoc[2], "%Y-%m-%d"
            ).date() < datetime.datetime.now().date() + datetime.timedelta(days=90):
                self.medocs_expire_in_tree_month.append(medoc)
            if 0 < medoc[1] < 50:
                self.medocs_qte_inf_50.append(medoc)
            if medoc[1] <= 0:
                self.medocs_qte_inf_0.append(medoc)
        nombre_notifications = (
            bool(self.medocs_expire_in_one_week)
            + bool(self.medocs_expire_in_one_month)
            + bool(self.medocs_expire_in_two_month)
            + bool(self.medocs_expire_in_tree_month)
            + bool(self.medocs_qte_inf_50)
            + bool(self.medocs_qte_inf_0)
            + bool(self.medocs_expired)
        )
        # actualiser le nombre de notifications
        try:
            self.notifications_button.badge.text = str(nombre_notifications)
            # self.notifications_button.update()
        except Exception as e:
            print(f"Error updating notifications button: {e}")
        self.__add_notifications()

    def __add_notifications(self):
        self.body.content = Column(
            expand=True,
            scroll=ScrollMode.ALWAYS,
            controls=[
                ResponsiveRow(
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.START,
                    controls=[
                        self.__custom_expention_tile(
                            "Produits expirés\n",
                            f"{len(self.medocs_expired)} produits sont expirés\n",
                            self.medocs_expired,
                        ),
                        self.__custom_expention_tile(
                            "Produits expirant dans une semaine",
                            f"{len(self.medocs_expire_in_one_week)} produits expirent dans une semaine",
                            self.medocs_expire_in_one_week,
                        ),
                        self.__custom_expention_tile(
                            "Produits expirant dans un mois",
                            f"{len(self.medocs_expire_in_one_month)} produits expirent dans un mois",
                            self.medocs_expire_in_one_month,
                        ),
                    ],
                ),
                ResponsiveRow(
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.START,
                    controls=[
                        self.__custom_expention_tile(
                            "Produits expirant dans deux mois",
                            f"{len(self.medocs_expire_in_two_month)} produits expirent dans deux mois",
                            self.medocs_expire_in_two_month,
                        ),
                        self.__custom_expention_tile(
                            "Produits expirant dans trois mois",
                            f"{len(self.medocs_expire_in_tree_month)} produits expirent dans trois mois",
                            self.medocs_expire_in_tree_month,
                        ),
                        self.__custom_expention_tile(
                            "Produits avec une quantité inférieure à 50",
                            f"{len(self.medocs_qte_inf_50)} produits avec une quantité inférieure à 50",
                            self.medocs_qte_inf_50,
                        ),
                    ],
                ),
                ResponsiveRow(
                    alignment=MainAxisAlignment.SPACE_AROUND,
                    vertical_alignment=CrossAxisAlignment.START,
                    controls=[
                        self.__custom_expention_tile(
                            "Produits en rupture de stock",
                            f"{len(self.medocs_qte_inf_0)} produits en rupture de stock",
                            self.medocs_qte_inf_0,
                        ),
                    ],
                ),
            ],
        )
        # try:
        #     self.body.update()
        # except Exception as e:
        #     print(f"Error updating body on Notification: {e}")

    def __custom_expention_tile(self, title: str, subtitle: str, medocs: list):
        # medocs = medocs if medocs else []
        return Container(
            col={"xs": 12, "sm": 6, "md": 4, "lg": 3.5},
            padding=padding.all(0),
            content=ExpansionTile(
                title=Text(
                    title.upper(), size=14, weight=FontWeight.BOLD, color="blue"
                ),
                subtitle=Text(subtitle, size=12),
                affinity=TileAffinity.TRAILING,
                expand=True,
                controls=[
                    Column(
                        scroll=ScrollMode.ALWAYS,
                        expand=True,
                        controls=[
                            ListTile(
                                title=Text(medoc[0], size=12),
                                subtitle=Text(
                                    f"Quantité : {medoc[1]}\nDate d'expiration : {medoc[2]}",
                                    size=11,
                                ),
                            )
                            for medoc in medocs
                        ],
                        height=200,
                        tight=True,
                    )
                ],
                shape=RoundedRectangleBorder(10),
                collapsed_shape=RoundedRectangleBorder(10),
                dense=True,
            ),
            shadow=BoxShadow(blur_radius=2, color="#DADADA"),
            border_radius=border_radius.all(15),
            bgcolor="white",
            border=border.all(1, color="#FD0F0F") if medocs else None,
            badge=(
                Badge(
                    text=str(len(medocs)),
                    bgcolor="red",
                    text_style=TextStyle(size=12),
                    padding=padding.all(5),
                )
                if medocs
                else None
            ),
        )
