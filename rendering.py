from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QColor, QPen
from main import *


class BmpRenderer(QWidget):
    def __init__(self, file, header, bitmap_info, parent=None):
        QWidget.__init__(self, parent)
        self.bitmap_info = bitmap_info
        self.file = file
        self.header = header
        self.pixel_offset = header.offset
        self.row_offset = 0
        self.x = 0
        self.y = bitmap_info.height - 1
        self.setGeometry(200, 200, max(0, 200), max(0   ,200))
        self.qp=QPainter()
        self.show()

    def paintEvent(self, e):
        # qp = QPainter()
        # self.__init__(self.file,self.header,self.bitmap_info)
        self.pixel_offset = self.header.offset
        self.row_offset = 0
        self.x = 0
        self.y = self.bitmap_info.height - 1
        self.qp.begin(self)
        self.render_24bit(self.qp, self.file, self.header, self.bitmap_info)
        self.qp.end()


    def render_24bit(self, qp: QPainter, file: bytes, header: FileHeader, bitmap: BitmapInfoVersion3):
        for pixel in self.get_next_pixel(file):
            coords, color = pixel
            qp.setPen(QColor(*color))
            qp.drawPoint(*coords)

    def get_next_pixel(self, file: bytes):
        while self.y >= 0:
            blue = unpack('B', file[self.pixel_offset:self.pixel_offset + 1])[0]
            green = unpack('B', file[self.pixel_offset + 1:self.pixel_offset + 2])[0]
            red = unpack('B', file[self.pixel_offset + 2:self.pixel_offset + 3])[0]
            self.pixel_offset += 3
            self.row_offset += 3
            yield (self.x, self.y), (red, green, blue)
            self.x = (self.x + 1) % self.bitmap_info.width

            if self.row_offset >= self.bitmap_info.width * 3:
                while self.row_offset % 4 != 0:
                    self.pixel_offset += 1
                    self.row_offset += 1
                else:
                    self.y -= 1
                    self.x = 0
                    self.row_offset = 0
