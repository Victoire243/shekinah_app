from components.CustomTextField import CustomTextField
import shutil
from flet import (
    Page,
    Container,
    padding,
    alignment,
    DecorationImage,
    ImageFit,
    ColorFilter,
    BlendMode,
    Colors,
    Button,
    ButtonStyle,
    RoundedRectangleBorder,
    Column,
    MainAxisAlignment,
    CrossAxisAlignment,
    Image,
    Text,
    SnackBar,
    border_radius,
    GestureDetector,
)
from pathlib import Path


class LoginView(Container):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.alignment = alignment.center
        self.padding = padding.symmetric(vertical=50, horizontal=50)
        self.image = DecorationImage(
            src=str(Path(__file__).parent.parent.resolve()).replace("\\", "/")
            + "/assets/images/bg_image.jpg",
            fit=ImageFit.COVER,
            color_filter=ColorFilter(
                color=Colors.with_opacity(0.5, "black"), blend_mode=BlendMode.MULTIPLY
            ),
        )
        self.username = CustomTextField(label="Nom d'utilisateur", height=60)
        self.password = CustomTextField(
            label="Mot de passe",
            password=True,
            can_reveal_password=True,
            height=60,
            on_submit=self.__se_connecter,
        )
        self.button = Button(
            "Connexion",
            elevation=1,
            style=ButtonStyle(
                shape=RoundedRectangleBorder(10),
                color="white",
                bgcolor="blue",
            ),
            height=60,
            on_click=self.__se_connecter,
        )
        self.content = Container(
            width=500,
            padding=padding.symmetric(vertical=20, horizontal=30),
            border_radius=border_radius.all(10),
            bgcolor="#C4CAFF",
            content=Column(
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.STRETCH,
                controls=[
                    Image(
                        src=str(Path(__file__).parent.parent.resolve()).replace(
                            "\\", "/"
                        )
                        + "/assets/images/logo_shekinah_.png",
                        height=150,
                    ),
                    GestureDetector(
                        content=Text(
                            value="Pharmacie Shekinah",
                            size=20,
                            color="black",
                            text_align="center",
                            weight="bold",
                        ),
                        on_double_tap=self.__copy_db,
                    ),
                    self.username,
                    self.password,
                    self.button,
                ],
            ),
        )

    def __se_connecter(self, e):
        if self.username.value == "SHEKI" and self.password.value == "2022":
            self.page.go("/home")
        else:
            if self.page.overlay:
                self.page.overlay.clear()
            self.page.overlay.append(
                SnackBar(
                    Text("Nom d'utilisateur ou mot de passe incorrect"),
                    open=True,
                )
            )
            self.page.update()

    def __copy_db(self, e):
        db = (
            str(Path(__file__).parent.parent.resolve()).replace("\\", "/")
            + "/assets/db/db_test.sqlite3"
        )
        drafts = (
            str(Path(__file__).parent.parent.resolve()).replace("\\", "/")
            + "/assets/drafts/drafts.df"
        )
        home_dir = str(Path.home()).replace("\\", "/")
        try:
            shutil.copy(db, home_dir + "/db_test.sqlite3")
        except:
            pass
        try:
            shutil.copy(drafts, home_dir + "/drafts.df")
        except:
            pass
