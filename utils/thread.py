import subprocess

from PyQt5.QtCore import QThread, pyqtSignal

from utils.mc import listen


class LanThread(QThread):
    breakSignal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def run(self):
        port, content = listen()
        self.breakSignal.emit(port, content)


class FrpThread(QThread):
    breakSignal = pyqtSignal(str)

    def __init__(self, thread):
        super().__init__()
        self.pthread = thread

    def run(self):
        self.pthread.wait()
        p = subprocess.Popen(
            ['frpc', '-c', 'mc.ini'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        while p.poll() is None:
            if p.stdout:
                line = p.stdout.readline().decode('utf-8').strip()
                self.breakSignal.emit(line)
