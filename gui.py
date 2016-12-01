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
        self.dockwidget = QtWidgets.QDockWidget(self)
        self.dockwidget.hide()
        self.init_ui()
        if self.file_name is not None and self.file_name != '':
            self.openFile(self.file_name)

    def init_ui(self):
        open_action = QtWidgets.QAction("&Open", self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)

        close_action = QtWidgets.QAction("&Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(lambda x: sys.exit())

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        self.dockwidget.setWidget(InfoWidget())
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockwidget)

        self.setWindowTitle('BMP file opener')
        self.show()

    def openFile(self, name=None):
        if name == '' or name is None or name is False:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file')[0]
            if filename == '':
                return
            self.file_name = filename
        try:
            with open(self.file_name, 'rb') as file:
                self.file_name = self.file_name
                self.file_data = open_file(self.file_name)
                self.file_info = read_file_header(self.file_data, self.file_name)
                self.bitmap_info = get_bitmap_info(self.file_data,self.file_info)
                self.file_info.name = self.file_name
                check_if_file_is_bmp(self.file_data, self.file_name)
        except Exception as e:
            self.show_error(e)
        else:
            self.dockwidget.widget().show_file_info(self.file_info)
            # label = QtWidgets.QLabel(self)
            # label.setPixmap(QPixmap(self.file_name))
            renderer = BmpRenderer(self.file_data,self.file_info,self.bitmap_info)
            renderer.setGeometry(200, 200, max(0, 200), max(0,200))
            # renderer.exec_()
            self.setCentralWidget(renderer)
            self.centralWidget().setGeometry(200,200,200,200)
            # self.centralWidget().qp.setViewport(200, 200, max(0, 200), max(0, 200))
            self.move(200,200)
            self.centralWidget().render(self, QPoint(100,100))
            self.dockwidget.show()
            self.showMaximized()

    # def moveEvent(self,e):
        # if self.centralWidget() is not None:
        #     self.centralWidget().paintEvent(e)

    def show_error(self, error):
        messagebox = QMessageBox()
        messagebox.setIcon(QMessageBox.Critical)
        messagebox.setWindowTitle("Error")
        messagebox.setStandardButtons(QMessageBox.Close)
        messagebox.setText(str(error))
        messagebox.exec_()


class InfoWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.layout = QtWidgets.QGridLayout()
        self.name_label = QLabel()
        self.size_label = QLabel()
        self.offset_label = QLabel()
        self.version_label = QLabel()
        self.init_ui()

    def init_ui(self):
        name = QLabel('Name: ')
        size = QLabel('Size: ')
        offset = QLabel('Offset: ')
        version = QLabel('Version: ')
        titles = [name, size, offset, version]
        for i in range(len(titles)):
            self.layout.addWidget(titles[i], i, 0)
        values = [self.name_label, self.size_label, self.offset_label, self.version_label]
        for i in range(len(values)):
            self.layout.addWidget(values[i], i, 1)
            self.layout.setRowStretch(i, 0)
        self.layout.addWidget(QWidget(), len(values), 0, -1, -1)
        self.layout.setRowStretch(len(values), 1)
        self.setLayout(self.layout)

    def show_file_info(self, info):
        self.name_label.setText(info.name)
        self.offset_label.setText('{} bytes'.format(info.offset))
        self.size_label.setText('{} bytes'.format(info.size))
        self.version_label.setText(str(info.version))
