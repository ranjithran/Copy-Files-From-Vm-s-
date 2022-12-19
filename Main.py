from urllib.parse import parse_qs, urlparse

import flet
from flet import *
from flet import colors, dropdown, icons, padding
from Views import home


class Main(UserControl):
    def __init__(self):
        super().__init__()
        self.username = Ref[TextField]()
        self.password = Ref[TextField]()

    def login(self, e):
        if (self.username.current.value == ''):
            self.username.focus()
            return
        if (self.password.current.value == ''):
            self.password.focus()
            return
        self.page.go("mid", username=self.username.current.value,
                     password=self.password.current.value)

    def build(self):
        return Column(
            controls=[Row(
                vertical_alignment=CrossAxisAlignment.CENTER,

                controls=[
                    Column(
                        controls=[TextField(ref=self.username, label="UserName", border_color=colors.PURPLE),
                                  TextField(ref=self.password, label="Password",
                                            password=True, border_color=colors.PURPLE),
                                  ElevatedButton(
                            text="Login", on_click=self.login,
                            bgcolor=colors.PURPLE,
                            color=colors.WHITE),
                        ],
                    ),
                ],
                alignment=MainAxisAlignment.CENTER,
            )]
        )


class Mid(UserControl):
    def __init__(self):
        super().__init__()

    def onDownload(self, e):
        self.page.go("home", mtype=True)

    def onUpload(self, e):
        self.page.go("home", mtype=False)

    def build(self):
        return Container(
            content=Row(
                alignment='center',
                controls=[
                    ElevatedButton(
                        "Download",
                        icon=icons.UPLOAD,
                        on_click=self.onDownload,
                        bgcolor=colors.PURPLE_ACCENT,
                        color=colors.WHITE,
                    ), ElevatedButton(
                        "Upload",
                        icon=icons.DOWNLOAD,
                        bgcolor=colors.PURPLE_ACCENT,
                        on_click=self.onUpload,
                        color=colors.WHITE,
                    ),
                ]
            ),
        )


def main(page: Page):

    # def logout(e):
    #     nonlocal isusernameandpasswordSetted
    #     isusernameandpasswordSetted = False
    #     toppage = page.views[0]
    #     page.views.clear()
    #     page.views.append(toppage)
    #     page.update()

    page.title = "Upload Files To vm"

    isusernameandpasswordSetted = False
    # create application instance

    app = Main()

    # add application's root control to the page
    page.add(app)
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    page.vertical_alignment = MainAxisAlignment.CENTER
    file_picker = FilePicker()
    page.overlay.append(file_picker)
    page.update()
    username = ""
    password = ""

    def onRouteChange(e):
        nonlocal isusernameandpasswordSetted, username, password, file_picker

        parserdurl = urlparse(e.data)
        parameters = parse_qs(parserdurl.query)
        mtype = ''
        print(f"Navigate to /{parserdurl.path} with parameter of {parameters}")

        if (not isusernameandpasswordSetted and 'username' in parameters and 'password' in parameters):
            username = parameters["username"][0]
            password = parameters["password"][0]
            isusernameandpasswordSetted = False
        if 'mtype' in parameters:
            mtype = True if parameters['mtype'][0] == 'True' else False

        if (parserdurl.path == "home"):
            page.views.append(View(
                "/home",
                [
                    home.Home(username, password,
                              filepicker=file_picker, mtype=mtype)
                ],
                vertical_alignment="center",
                horizontal_alignment="center", appbar=AppBar(title=Text("Upload files to vm's"), leading_width=40, bgcolor=colors.PURPLE, center_title=True, )),
            )
        if (parserdurl.path == 'mid'):
            page.views.append(View(
                "/mid",
                [
                    Mid()
                ],
                vertical_alignment="center",
                horizontal_alignment="center", appbar=AppBar(title=Text("Upload files to vm's"), leading_width=40, bgcolor=colors.PURPLE, center_title=True, )),
            )
        page.update()

    def onViewPop(e):
        page.views.pop()
        top_view = page.views[len(page.views)-1]
        page.go(top_view.route)

    page.on_route_change = onRouteChange
    page.on_view_pop = onViewPop


flet.app(target=main)
