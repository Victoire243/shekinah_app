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
    ):
        super().__init__()
        self.__calcul_totaux = calcul_totaux
        self.nom = Text(nom, weight=FontWeight.BOLD, col=4)
        self.quantite = CustomTextField(
            input_filter=NumbersOnlyInputFilter(),
            col=1,
            value=quantite,
            on_change=self.__update_prix_total,
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
                                Text("FC"),
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
