import subprocess
import time

from PyQt5.QtCore import QThread, pyqtSignal

from utils.mc import listen


class LanThread(QThread):
    breakSignal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def run(self):
        port, content = None, None
        while True:
            data = listen()
            if (port, content) != data:
                port, content = data
                self.breakSignal.emit(port, content)
                time.sleep(3)
            time.sleep(3)


class FrpThread(QThread):
    breakSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        p = subprocess.Popen(
            ['frpc', '-c', 'mc.ini'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        while p.poll() is None:
            if p.stdout:
                line = p.stdout.readline().decode('utf-8').strip()
                self.breakSignal.emit(line)
