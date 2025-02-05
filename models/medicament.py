from flet import (
    Container,
    Text,
    FontWeight,
    ResponsiveRow,
    Row,
    IconButton,
    Icons,
    InputFilter,
    NumbersOnlyInputFilter,
    border_radius,
    border,
    margin,
    padding,
    Column,
    MainAxisAlignment,
    CrossAxisAlignment,
)
from components.CustomTextField import CustomTextField


class Medicament(Container):
    def __init__(
        self,
        nom,
        quantite,
        forme,
        prix_unitaire,
        prix_total,
        medoc_delete,
        calcul_totaux=None,
        devise_initiale="FC",
    ):
        super().__init__()
        self.__calcul_totaux = calcul_totaux
        self.nom = Text(nom, weight=FontWeight.BOLD, col=4)
        self.quantite = CustomTextField(
            input_filter=NumbersOnlyInputFilter(),
            col=1,
            value=quantite,
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
        self.forme = CustomTextField(col=2, value=forme)
        self.prix_unitaire = CustomTextField(
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=2,
            value=prix_unitaire,
            on_change=self.__update_prix_total,
        )
        self.prix_total = Text(prix_total, weight=FontWeight.BOLD)
        self.medoc_delete = medoc_delete
        self.border_radius = border_radius.all(5)
        self.border = border.all(width=1, color="white")
        self.margin = margin.only(left=20, right=20, top=5, bottom=5)
        self.bgcolor = "#DBDBDB"
        self.padding = padding.all(10)
        self.devise = Text(devise_initiale, weight=FontWeight.BOLD, col=1)
        self.content = ResponsiveRow(
            controls=[
                self.nom,
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
                                self.devise,
                            ],
                        ),
                        IconButton(
                            icon=Icons.DELETE,
                            icon_color="red",
                            on_click=self.__delete,
                        ),
                    ],
                ),
            ]
        )

    def __update_prix_total(self, e):
        self.prix_total.value = str(
            round(
                float(self.prix_unitaire.value if self.prix_unitaire.value else 0)
                * float(self.quantite.value if self.quantite.value else 0),
                3,
            )
        )
        self.prix_total.update()
        self.__calcul_totaux()

    def __delete(self, e):
        self.medoc_delete(self)

    def handler_devise_change(self, devise, taux):
        self.prix_unitaire.value = str(
            round(
                float(self.prix_unitaire.value if self.prix_unitaire.value else 0)
                / taux,
                3,
            )
        )
        self.devise.value = devise
        self.devise.update()
        self.prix_unitaire.update()
        self.__update_prix_total(None)

    def __incrise_quantite(self, e):
        self.quantite.value = (
            str(int(self.quantite.value) + 1) if self.quantite.value else 1
        )
        self.quantite.update()
        self.__update_prix_total(None)

    def __desincrise_quantite(self, e):
        if self.quantite.value and int(self.quantite.value) > 0:
            self.quantite.value = str(int(self.quantite.value) - 1)
        else:
            self.quantite.value = "0"
        self.quantite.update()
        self.__update_prix_total(None)
