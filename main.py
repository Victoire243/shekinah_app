from views.login_view import LoginView
from views.accueil_view import AccueilView

from pathlib import Path
from db.db_utils import DBUtils
from flet import (
    Text,
    MainAxisAlignment,
    padding,
    Theme,
    RouteChangeEvent,
    AlertDialog,
    MainAxisAlignment,
    Page,
    app,
    ElevatedButton,
    OutlinedButton,
    View,
)

# import logging

# logging.basicConfig(level=logging.DEBUG)


current_directory = (
    str(Path(__file__).parent.resolve()).replace("\\", "/")
    + "/assets/db/db_test.sqlite3"
)


db = DBUtils(current_directory)
# list_medocs_names = db.get_all_medocs_list()
# list_medocs_for_preview = db.get_medocs_for_list_preview()


def main(page: Page):
    def on_route_change(route: RouteChangeEvent):
        page.views.clear()
        page.views.append(
            View(
                "/",
                [
                    LoginView(page),
                ],
                padding=padding.all(0),
            )
        )
        if page.route == "/home":
            page.views.append(
                View(
                    "/home",
                    [
                        AccueilView(page, db),
                    ],
                    padding=padding.all(0),
                )
            )
        try:
            page.update()
        except Exception as e:
            print(f"Error updating page: {e}")

    def on_view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    def yes_click(e):
        db.close()
        page.window.destroy()
        # page.update()

    def no_click(e):
        page.close(confirm_dialog)

    page.padding = padding.all(0)
    page.title = "PHARMACIE SHEKINA"
    page.bgcolor = "#f0f0f0"
    page.fonts = {
        "Poppins": str(Path(__file__).parent.resolve()).replace("\\", "/")
        + "/assets/fonts/Poppins/Poppins-Regular.ttf",
    }
    page.theme = Theme(font_family="Poppins")
    page.window.center()
    page.window.maximized = True
    # page.window.prevent_close = True
    # page.window.on_event = handle_window_event

    confirm_dialog = AlertDialog(
        modal=True,
        title=Text("Veuillez confirmer"),
        content=Text("Voulez-vous quitter ?"),
        actions=[
            ElevatedButton("Oui, quitter", on_click=yes_click),
            OutlinedButton("Non, annuler", on_click=no_click),
        ],
        actions_alignment=MainAxisAlignment.END,
    )

    page.on_route_change = on_route_change
    page.on_view_pop = on_view_pop
    page.go(page.route)


app(
    main,
    assets_dir=str(Path(__file__).parent.resolve()).replace("\\", "/") + "/assets",
)
