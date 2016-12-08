import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QMessageBox, QDialog

from rendering import *


class MainWidget(QtWidgets.QMainWindow):
    def __init__(self, filename=None, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.file_name = filename
        self.color_table = None
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

        palette_action = QtWidgets.QAction("&Show palette", self)
        palette_action.setShortcut('Ctrl+P')
        palette_action.triggered.connect(self.show_palette)

        info_action = QtWidgets.QAction("&Show info", self)
        info_action.setShortcut('Ctrl+I')
        info_action.triggered.connect(
            lambda: self.dock_widget.show() if self.dock_widget.isHidden() else self.dock_widget.hide())

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)
        menu_bar.addAction(palette_action)
        menu_bar.addAction(info_action)

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
                if self.bitmap_info.bit_count <= 8:
                    self.color_table = extract_palette(self.file_data, self.bitmap_info)
        except Exception as e:
            self.show_error(e)
        else:
            self.dock_widget.setWidget(InfoWidget())
            self.dock_widget.widget().show_file_info(self.file_info, self.bitmap_info)
            renderer = BmpRenderer(self.file_data, self.file_info, self.bitmap_info, self.color_table)
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

    def show_palette(self):
        if not self.file_name or self.bitmap_info.bit_count > 8:
            return
        palette = group_palette_by(self.color_table, 8)
        palette_drawer = PaletteWidget(palette)
        palette_drawer.setGeometry(200, 100, 700, 200)
        palette_drawer.exec_()


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
                title.setAlignment(QtCore.Qt.AlignRight)
                value = QLabel()
                title.setText(prop[0])
                value.setText(str(prop[1]))
                self.layout.addWidget(title, row, 0)
                self.layout.addWidget(value, row, 1)
                row += 1
        self.layout.addWidget(QWidget(), row, 0, -1, -1)
        self.layout.setRowStretch(row, 1)
        self.setLayout(self.layout)


class PaletteWidget(QDialog):
    def __init__(self, palette, parent=None):
        QWidget.__init__(self, parent)
        self.palette = palette

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_palette(painter, self.palette)
        painter.end()

    def draw_palette(self, painter: QPainter, palette):
        rect_size = 20
        for i in range(len(palette)):
            row = palette[i]
            for j in range(len(row)):
                color = row[j]
                # painter.setBrush(QColor(*color))
                painter.fillRect(i * rect_size, j * rect_size, rect_size, rect_size, QColor(*color))
