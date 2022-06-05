import os

import psutil
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget

from utils.config import Config
from utils.thread import LanThread, FrpThread


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.config = Config()
        self.thread = None
        self.frp_thread = None

        widget = QWidget()
        widget.setLayout(QtWidgets.QVBoxLayout())
        widget.setMinimumSize(800, 500)
        widget.setStyleSheet("QWidget{border:1px solid #014F84}")
        self.setCentralWidget(widget)

        widget.layout().addWidget(self.control_panel(widget))
        widget.layout().addWidget(self.log_panel(widget))

    def control_panel(self, parent):
        panel = QWidget(parent)
        panel.setLayout(QtWidgets.QHBoxLayout())
        panel.setMinimumSize(0, 0)
        panel.setContentsMargins(0, 0, 0, 0)
        panel.layout().addWidget(self.server_config(panel))
        panel.layout().addWidget(self.client_config(panel))
        panel.layout().addWidget(self.operation(panel))
        return panel

    def server_config(self, parent):
        panel = QWidget(parent)
        panel.setLayout(QtWidgets.QVBoxLayout())
        panel.setStyleSheet("QWidget{border-style:none}")
        panel.layout().setContentsMargins(0, 0, 0, 0)

        panel.layout().addWidget(self.input_config_item(panel, "访问地址:", "server_addr"))
        panel.layout().addWidget(self.input_config_item(panel, "通讯端口:", "server_port"))
        panel.layout().addWidget(self.input_config_item(panel, "通讯密钥:", "token"))
        return panel

    def client_config(self, parent):
        panel = QWidget(parent)
        panel.setLayout(QtWidgets.QVBoxLayout())
        panel.setStyleSheet("QWidget{border-style:none}")
        panel.layout().setContentsMargins(0, 0, 0, 0)

        panel.layout().addWidget(self.input_config_item(panel, "本地端口:", "local_port"))
        panel.layout().addWidget(self.input_config_item(panel, "远程端口:", "remote_port"))
        return panel

    def operation(self, parent):
        panel = QtWidgets.QWidget(parent)
        panel.setLayout(QtWidgets.QVBoxLayout())
        panel.layout().setSpacing(0)

        button = QtWidgets.QPushButton(parent)
        button.setText("启动")
        button.setObjectName("button")
        button.setStyleSheet(
            """
            QPushButton {
                font: 700 16pt;
                background-color: rgb(255, 255, 255);
            }
            QPushButton:hover {
                color: rgb(0, 0, 0);
            }
            QPushButton:pressed {
                background-color: rgb(255, 255, 255);
            }
            """
        )
        button.clicked.connect(lambda: self.button_clicked_event(button))
        panel.layout().addWidget(button)
        return panel

    def input_config_item(self, parent, title, name):
        panel = QtWidgets.QWidget(parent)
        panel.setLayout(QtWidgets.QHBoxLayout())
        panel.setStyleSheet("QWidget{border-style:groove}")

        label = QtWidgets.QLabel(panel)
        label.setText(title)
        label.setStyleSheet("QWidget{border-style:none}")

        input_box = QtWidgets.QLineEdit(parent)
        input_box.setPlaceholderText("")
        input_box.setObjectName(name)
        input_box.setText(getattr(self.config, name))
        input_box.setStyleSheet("QWidget{border-style:none}")
        input_box.textChanged.connect(self.config_changed_event)

        panel.layout().addWidget(label)
        panel.layout().addWidget(input_box)
        return panel

    @staticmethod
    def log_panel(parent):
        panel = QtWidgets.QWidget(parent)
        panel.setMinimumSize(800, 200)
        panel.setLayout(QtWidgets.QHBoxLayout())
        panel.layout().setContentsMargins(0, 0, 0, 0)
        panel.layout().setSpacing(0)

        logger = QtWidgets.QTextBrowser(panel)
        logger.setObjectName("logger")
        logger.thread()

        panel.layout().addWidget(logger)
        return panel

    def config_changed_event(self):
        items = self.window().findChildren(QtWidgets.QLineEdit)
        for item in items:
            self.config.update({item.objectName(): item.text()})

    def button_clicked_event(self, button):
        if button.text() == '启动':
            button.setText('停止')
            self.window().findChild(QtWidgets.QTextBrowser, "logger").clear()
            self.thread = LanThread()
            self.process_log('[Client: "start listening ..."]')
            self.thread.breakSignal.connect(self.process_local_port)
            self.thread.start()
        else:
            self.close_thread()
            self.close_frp()
            button.setText('启动')

    def close_thread(self):
        self.thread.terminate()
        self.thread.quit()
        for x in psutil.Process(os.getpid()).children(recursive=True):
            x.kill()
        self.thread = None

    def close_frp(self):
        if not self.frp_thread:
            return
        self.frp_thread.terminate()
        self.frp_thread.quit()
        for x in psutil.Process(os.getpid()).children(recursive=True):
            x.kill()
        self.frp_thread = None

    def process_local_port(self, port, content):
        port_edit = self.window().findChild(QtWidgets.QLineEdit, "local_port")
        if port_edit.text() != port:
            port_edit.setText(port)
            self.process_log('\n[Client: "port has been changed to {}"]'.format(port))
        self.process_log(content)
        if port_edit.text() != port:
            self.close_frp()
            self.frp_thread = FrpThread()
            self.frp_thread.breakSignal.connect(self.process_log)
            self.frp_thread.start()

    def process_log(self, log):
        logger = self.window().findChild(QtWidgets.QTextBrowser, "logger")
        logger.insertPlainText(log + '\n')
