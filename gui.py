from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import QPoint
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from main import *
from rendering import *
import sys


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, filename=None, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file_name = filename
        self.dock_widget = QtWidgets.QDockWidget(self)
        self.dock_widget.hide()
        self.init_ui()
        if self.file_name is not None and self.file_name != '':
            self.open_file(self.file_name)

    def init_ui(self):
        open_action = QtWidgets.QAction("&Open", self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)

        close_action = QtWidgets.QAction("&Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(lambda x: sys.exit())

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        self.dock_widget.setWidget(InfoWidget())
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_widget)

        self.setWindowTitle('BMP file opener')
        self.show()

    def open_file(self, name=None):
        if name == '' or name is None or name is False:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file')[0]
            if filename == '':
                return
            self.file_name = filename
        try:
            with open(self.file_name, 'rb') as file:
                self.file_name = self.file_name
                self.file_data = open_file(self.file_name)
                check_if_file_is_bmp(self.file_data, self.file_name)
                self.file_info = read_file_header(self.file_data, self.file_name)
                self.bitmap_info = get_bitmap_info(self.file_data, self.file_info)
                self.file_info.name = self.file_name
        except Exception as e:
            self.show_error(e)
        else:
            self.dock_widget.widget().show_file_info(self.file_info, self.bitmap_info)
            renderer = BmpRenderer(self.file_data, self.file_info, self.bitmap_info)
            self.setCentralWidget(renderer)
            self.dock_widget.show()
            self.showMaximized()

    def show_error(self, error):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Critical)
        message_box.setWindowTitle("Error")
        message_box.setStandardButtons(QMessageBox.Close)
        message_box.setText(str(error))
        message_box.exec_()


class InfoWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QtWidgets.QGridLayout()
        self.name_label = QLabel()
        self.size_label = QLabel()
        self.offset_label = QLabel()
        self.version_label = QLabel()
        self.bitmap_label = QLabel()

    def show_file_info(self, header: FileHeader, bitmap_info: BitmapInfoVersion3):
        row = 0
        self.layout = QtWidgets.QGridLayout()
        for source in [header, bitmap_info]:
            for prop in source:
                title = QLabel()
                value = QLabel()
                title.setText(prop[0])
                value.setText(str(prop[1]))
                self.layout.addWidget(title, row, 0)
                self.layout.addWidget(value, row, 1)
                row += 1
        self.layout.addWidget(QWidget(), row, 0, -1, -1)
        self.layout.setRowStretch(row, 1)
        self.setLayout(self.layout)
