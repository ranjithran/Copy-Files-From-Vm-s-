from paramiko import SSHClient
from scp import SCPClient
import paramiko
from stat import S_ISDIR, S_ISREG
import traceback

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class sshClientCom(metaclass=SingletonMeta):

    def connect(self):
        try:
            self.ssh = SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print(f"Url --> {self.url} | UserName -->{self.username} | password -->{self.password}")
            self.ssh.connect(self.url, username=self.username,
                             password=self.password,port=22)
            self.connected = True

        except Exception as ex:
            print(ex)
            self.connected = False
            raise ex

    def __init__(self, username: str, password: str, url: str, userTmpFolder: str, ):
        self.username = username
        self.password = password
        self.url = url
        self.userTmpFolder = userTmpFolder
        self.mainDist = ""
        self.connected = False

    def uploadFile(self, dist: str, src, progressCallBack, serverAccountName: str):
        try:
            if not self.connected:
                self.connect()
            if self.connected:
                self.mainDist = dist if dist[len(dist)-1] == '/' else dist+'/'
                self.serverAccountName = serverAccountName
                self.ssh.exec_command("mkdir ~/tmp/")
                scp = SCPClient(self.ssh.get_transport(),
                                progress=progressCallBack)
                scp.put(list(src.values()), self.userTmpFolder, recursive=True)
                self.changeToMainPath(src)
        except Exception as e:
            raise e

    def changeToMainPath(self, files):
        try:
            
            commands = f"sudo -iu root bash -c '"
            for i in files.keys():
                commands += f"cp /home/{self.setUsername()}/tmp/{i}  {self.mainDist};"
                commands += f'chmod 664 {self.mainDist}{i}; chown {self.serverAccountName} {self.mainDist}{i};'
            commands += " echo \"completed\"; '"
            print(commands)
            session = self.ssh.get_transport().open_session()
            session.set_combine_stderr(True)
            session.get_pty()
            session.exec_command(commands)
            stdin = session.makefile('wb', -1)
            stdout = session.makefile('rb', -1)
            stdin.write(self.password + '\n')
            stdin.flush()
            print(stdout.read().decode("utf-8"))

        except Exception as e:
            raise e

    def downloadFile(self, fileNames, progressCallBack,pathtoSave):
        try:
            if not self.connected:
                self.connect()
            if self.connected:
                files = []
                self.ssh.exec_command(f"mkdir /home/{self.setUsername()}/tmp/")
                commands = f"sudo -iu root bash -c '"
                for n, i in fileNames.items():
                    tmp = f"/home/{self.setUsername()}/tmp/"
                    commands += f"cp {i} {tmp} ;"
                    commands += f'chmod 775 /home/{self.setUsername()}/tmp/{n}; chown {self.setUsername()} /home/{self.setUsername()}/tmp/{n};'
                    files.append(f"{tmp}{n}")
                commands += " echo \"completed\"; '"
                print(commands)
                session = self.ssh.get_transport().open_session()
                session.set_combine_stderr(True)
                session.get_pty()
                session.exec_command(commands)
                stdin = session.makefile('wb', -1)
                stdout = session.makefile('rb', -1)
                stdin.write(self.password + '\n')
                stdin.flush()
                print(stdout.read().decode("utf-8"))
                scp = SCPClient(self.ssh.get_transport(),
                                progress=progressCallBack)
                scp.get(files, recursive=True,local_path=pathtoSave)
            else:
                raise Exception("Unable to login")
        except Exception as e:
            traceback.print_exc()
            print(e)
            raise e

    def setUsername(self):
        username=self.username
        if '@' in self.username:
            username=(self.username.split("@")[1]+'/'+self.username.split("@")[0])
        return username            