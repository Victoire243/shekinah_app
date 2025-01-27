from flet import *
from components.CustomTextField import CustomTextField


class MedicamentEntree(Container):
    def __init__(
        self,
        nom,
        quantite,
        forme,
        prix_unitaire_achat,
        prix_unitaire_vente,
        prix_total_achat,
        prix_total_vente,
        medoc_delete,
        gain,
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
        self.forme = CustomTextField(col=1, value=forme)
        self.prix_unitaire_achat = CustomTextField(
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=1,
            value=prix_unitaire_achat,
            on_change=self.__update_prix_total,
        )
        self.prix_unitaire_vente = CustomTextField(
            input_filter=InputFilter(regex_string=r"^(\d*\.?\d+|\d+\.?\d*|\d*)$"),
            col=1,
            value=prix_unitaire_vente,
            on_change=self.__update_prix_total,
        )

        self.prix_total_achat = Text(prix_total_achat, weight=FontWeight.BOLD, col=1)
        self.prix_total_vente = Text(prix_total_vente, weight=FontWeight.BOLD, col=1)
        self.gain = Text(gain, weight=FontWeight.BOLD, col=1)
        self.medoc_delete = medoc_delete
        self.border_radius = border_radius.all(5)
        self.border = border.all(width=1, color="white")
        self.margin = margin.only(left=20, right=20, top=5, bottom=5)
        self.bgcolor = "#DBDBDB"
        self.padding = padding.all(10)
        self.content = ResponsiveRow(
            vertical_alignment=CrossAxisAlignment.CENTER,
            controls=[
                self.nom,
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
                        IconButton(
                            icon=Icons.DELETE,
                            icon_color="red",
                            on_click=self.__delete,
                        ),
                    ],
                ),
            ],
        )

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
        self.__calcul_totaux()
        self.gain.value = str(
            round(
                float(self.prix_total_vente.value) - float(self.prix_total_achat.value),
                3,
            )
        )
        self.gain.update()

    def __delete(self, e):
        self.medoc_delete(self)
