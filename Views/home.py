from flet import *
from .sshClient import sshClientCom
import flet
import subprocess


class Home(UserControl):

    def setupRefs(self):
        self.serverAccountName = Ref[TextField]()
        self.errorMsg = Ref[Text]()
        self.ipAddress = Ref[TextField]()
        if self.mtype:
            self.uploadListView = Ref[ListView]()
            self.distPath = Ref[TextField]()
            self.reftoUploadListChilds = {}
        else:
            self.downloadListView = Ref[ListView]()
            self.downloadFileName = Ref[TextField]()
            self.pathtoSave = Ref[TextField]()
            self.fileNamesTodownload = {}
            self.refDownloadListChildRef = {}

    def __init__(self, username: str, password: str, filepicker, mtype):
        super().__init__()
        self.username = username
        self.password = password
        self.sshClientCom = None
        self.filepicker = filepicker
        self.filesPaths = {}
        self.mtype = mtype
        self.setupRefs()

    def progress(self, filename, size, sent):
        if (float(sent)/float(size)*100 == 100):
            filename = mainName = str(filename)
            if self.mtype:
                filename = filename.split("'")[1]
                if filename in self.reftoUploadListChilds.keys():
                    self.reftoUploadListChilds[filename].current.leading = Icon(
                        icons.DONE, color=colors.GREEN)
            else:
                filename = filename.split("\\")
                filename = filename[len(filename)-1]
                if filename in self.fileNamesTodownload.keys():
                    tmp = self.refDownloadListChildRef[filename].current
                    tmp.leading = Icon(
                        icons.DONE, color=colors.GREEN)
                    tmp.trailing = IconButton(
                        icons.FOLDER, on_click=lambda e: [print(mainName), 
                        subprocess.Popen(f'explorer /select,{self.pathtoSave.current.value}/{mainName}')])
                    tmp.subtitle = Text(f"Saved at {mainName}")
            self.update()
        print(" -> %s progress: %.2f%%   \r" %
              (filename, float(sent)/float(size)*100))

    def onfileSelected(self, e):
        # self.listview.current.controls.clear

        if e.files:
            for x in e.files:
                self.filesPaths[x.name] = x.path
                listChildref = Ref[ListTile]()
                self.reftoUploadListChilds[x.name] = listChildref
                self.uploadListView.current.controls.append(
                    ListTile(
                        ref=listChildref,
                        title=Text(f"{x.name}"),
                        subtitle=Text(f"{x.path}"),
                    )
                )
        self.update()
        pass

    def onclickByFile(self, e):
        self.filepicker.on_result = self.onfileSelected
        self.filepicker.pick_files(
            allow_multiple=True
        )

    def showErrorMsg(self, msg: str):
        self.errorMsg.current.value = msg
        self.errorMsg.current.color = colors.RED_800

    def upload_m(self, e):
        if (self.ipAddress.current.value == ''):
            self.showErrorMsg("Please Enter Ip Address")
            self.ipAddress.current.focus()
            self.update()
            return
        if (self.serverAccountName.current.value == ''):
            self.showErrorMsg("Please Enter Service Name")
            self.serverAccountName.current.focus()
            self.update()
            return
        if (self.distPath.current.value == ""):
            self.showErrorMsg("Please Enter Destination Path")
            self.distPath.current.focus()
            self.update()
            return
        if (len(self.filesPaths.keys()) == 0):
            self.showErrorMsg(
                "Nothing to upload. Please choose something to upload")
            self.update()
            return
        try:
            # /home/userNames/
            self.sshClientCom = sshClientCom(
                username=self.username, password=self.password, url=self.ipAddress.current.value, userTmpFolder='~/tmp')
            self.sshClientCom.uploadFile(dist=self.distPath.current.value,
                                         src=self.filesPaths,
                                         progressCallBack=self.progress,
                                         serverAccountName=self.serverAccountName.current.value
                                         )
            self.errorMsg.current.value = "Update Permissions successfully"
            self.errorMsg.current.color = colors.GREEN
            self.update()
        except Exception as ex:
            self.showErrorMsg(str(ex))
            self.update()

    def downloadFiles_m(self, e):
        if (self.ipAddress.current.value == ''):
            self.showErrorMsg("Please Enter Ip Address")
            self.ipAddress.current.focus()
            self.update()
            return
        if (self.serverAccountName.current.value == ''):
            self.showErrorMsg("Please Enter Service Name")
            self.serverAccountName.current.focus()
            self.update()
            return
        if (len(self.fileNamesTodownload.keys()) == 0):
            self.showErrorMsg(
                "Nothing to download. Please choose something to download")
            self.update()
            return
        try:
            self.sshClientCom = sshClientCom(
                username=self.username, password=self.password, url=self.ipAddress.current.value, userTmpFolder='~/tmp')
            self.sshClientCom.downloadFile(
                fileNames=self.fileNamesTodownload, progressCallBack=self.progress, pathtoSave=self.pathtoSave.current.value)
            self.errorMsg.current.value = "Downloaded successfully, To open click on FolderIcon"
            self.errorMsg.current.color = colors.GREEN
            self.update()
        except Exception as ex:
            self.showErrorMsg(str(ex))
            self.update()

    def addToDownloadList(self, e):
        filedValue = self.downloadFileName.current.value
        self.downloadFileName.current.value = ''
        self.downloadFileName.current.focus()
        tmp = filedValue.split("/")

        if len(tmp) > 1:
            listChildref = Ref[ListTile]()
            fileName = tmp[len(tmp)-1]
            self.fileNamesTodownload[fileName] = filedValue
            self.refDownloadListChildRef[fileName] = listChildref
            self.downloadListView.current.controls.append(
                ListTile(
                    ref=listChildref,
                    title=Text(f"{fileName}"),
                    subtitle=Text(f"{filedValue}"),
                )
            )
        else:
            self.showErrorMsg('Unable to add List Please add full path name')
        self.update()

    def build(self):
        return Container(
            Column(
                controls=[
                    Text(ref=self.errorMsg, size=20),
                    TextField(ref=self.ipAddress,
                              label="Vm's Ip Address To connect",
                              border_color=colors.PURPLE_ACCENT,),

                    TextField(ref=self.serverAccountName,
                              label="Service Account name",

                              border_color=colors.PURPLE_ACCENT,
                              ),
                    TextField(ref=self.distPath,

                              border_color=colors.PURPLE_ACCENT,
                              label="Destination path, please give full path."),
                    Row(
                        controls=[
                            ElevatedButton(
                                "Pick files",
                                icon=icons.ATTACH_FILE_OUTLINED,
                                on_click=self.onclickByFile,
                                bgcolor=colors.PURPLE_ACCENT,
                                color=colors.WHITE,
                            ), ElevatedButton(
                                "Clear Files",
                                icon=icons.CLEAR_ALL_OUTLINED,
                                bgcolor=colors.PURPLE_ACCENT,
                                on_click=lambda e:[
                                    self.uploadListView.current.controls.clear(
                                    ), self.errorMsg.current.clean(), self.reftoUploadListChilds.clear(),
                                    self.filesPaths.clear(), self.update()],
                                color=colors.WHITE,
                            ),
                            ElevatedButton(
                                'Upload Files',
                                icon=icons.UPLOAD_FILE_OUTLINED,
                                on_click=self.upload_m,
                                bgcolor=colors.PURPLE_ACCENT,
                                color=colors.WHITE,
                            )

                        ]
                    ),
                    Container(
                        height=400,
                        content=ListView(expand=1, spacing=10,
                                         padding=20, ref=self.uploadListView)
                    ),
                ]
            ) if self.mtype else Column(
                controls=[
                    Text(ref=self.errorMsg, size=20),
                    TextField(ref=self.ipAddress,
                              label="Vm's Ip Address To connect",
                              border_color=colors.PURPLE_ACCENT,
                              hint_text='127.0.0.1'
                              ),
                    TextField(ref=self.pathtoSave,
                              label="Path to save",
                              border_color=colors.PURPLE_ACCENT,
                              ),
                    Row(
                        controls=[
                            TextField(ref=self.downloadFileName,
                                      label="FileName",
                                      border_color=colors.PURPLE_ACCENT,
                                      expand=True,
                                      hint_text='Ex: /home/username/pathtofile/text.txt',
                                      ),
                            ElevatedButton(
                                "Add Files to Download",
                                icon=icons.ADD,
                                bgcolor=colors.PURPLE_ACCENT,
                                on_click=self.addToDownloadList,
                                color=colors.WHITE,
                            ),
                        ]
                    ),
                    Row(
                        controls=[
                            ElevatedButton(
                                "Clear Files",
                                icon=icons.CLEAR_ALL_OUTLINED,
                                bgcolor=colors.PURPLE_ACCENT,
                                on_click=lambda e:[
                                    self.downloadListView.current.controls.clear(
                                    ), self.errorMsg.current.clean(), self.refDownloadListChildRef.clear(),
                                    self.fileNamesTodownload.clear(), self.update()],
                                color=colors.WHITE,
                            ),
                            ElevatedButton(
                                'Download Files',
                                icon=icons.UPLOAD_FILE_OUTLINED,
                                on_click=self.downloadFiles_m,
                                bgcolor=colors.PURPLE_ACCENT,
                                color=colors.WHITE,
                            ),

                        ]
                    ),
                    Container(
                        height=400,
                        content=ListView(expand=1, spacing=10,
                                         padding=20, ref=self.downloadListView)
                    ),
                ],
            )
        )


# def main(page: Page):
#     page.title = "ToDo App"
#     page.horizontal_alignment = "center"
#     page.update()
#     page.appbar = AppBar(title=Text("Ran"))
#     # create application instance
#     file_picker = FilePicker()
#     page.overlay.append(file_picker)
#     app = Home('username', 'password', filepicker=file_picker, mtype=False)

#     # add application's root control to the page
#     page.add(app)


# flet.app(target=main)
