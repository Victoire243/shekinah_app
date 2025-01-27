import flet as ft


class CustomDraftButton(ft.Row):
    def __init__(
        self, page: ft.Page, list_medocs, nom_client, date, delete_draft, load_draft
    ):
        super().__init__()
        self.page = page
        self.list_medicaments = list_medocs
        self.nom_client = nom_client
        self.delete_draft = delete_draft
        self.load_draft = load_draft
        self.date = date
        self.spacing = 10
        self.controls = [
            ft.Text(
                nom_client,
                size=12,
                color="blue",
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(
                date,
                size=12,
                color="blue",
            ),
            ft.IconButton(
                icon=ft.Icons.VISIBILITY,
                on_click=lambda e: self.load_draft(self),
                icon_color="green",
                icon_size=18,
                padding=ft.padding.all(0),
                height=25,
                width=25,
            ),
            ft.IconButton(
                icon=ft.Icons.DELETE_FOREVER,
                on_click=lambda e: self.delete_draft(self),
                icon_color="red",
                icon_size=18,
                padding=ft.padding.all(0),
                height=25,
                width=25,
            ),
        ]
