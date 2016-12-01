from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter, QColor, QPen
from main import *


class BmpRenderer(QWidget):
    def __init__(self, file, header, bitmap_info, parent=None):
        QWidget.__init__(self, parent)
        self.min_size = 200
        self.bitmap_info = bitmap_info
        self.file = file
        self.header = header
        self.pixel_offset = header.offset
        self.row_offset = 0
        self.x = 0
        self.y = bitmap_info.height - 1
        self.qp = QPainter()
        self.show()

    def paintEvent(self, e):
        self.pixel_offset = self.header.offset
        self.row_offset = 0
        self.x = 0
        self.y = self.bitmap_info.height - 1
        geom=self.geometry()
        self.qp.translate(geom.width()/2,geom.height()/2)
        self.qp.begin(self)

        if max(self.bitmap_info.width,self.bitmap_info.height)<self.min_size:
            self.render_small_picture(self.qp, self.file, self.min_size/self.bitmap_info.width)
        else:
            self.render_small_picture(self.qp, self.file, 1)
        self.qp.end()

    def render_24bit(self, qp: QPainter, file: bytes, header: FileHeader, bitmap: BitmapInfoVersion3):
        geom=qp.viewport() if self.qp.viewport() else self.qp.window()
        qp.translate(geom.width()/2,geom.height()/2)
        for pixel in self.get_next_pixel(file):
            coords, color = pixel
            qp.setPen(QColor(*color))
            qp.drawPoint(*coords)
        qp.translate(-200, -200)

    def render_small_picture(self, qp: QPainter, file, pixel_size):
        geom = qp.viewport() if self.qp.viewport() else self.qp.window()
        qp.translate((geom.width()-self.bitmap_info.width)/2, (geom.height()-self.bitmap_info.height) / 2)
        for pixel in self.get_next_small_pixel(file, pixel_size):
            coord, color = pixel
            qp.setPen(QColor(*color))
            qp.setBrush(QColor(*color))
            qp.drawRect(*coord, pixel_size, pixel_size)

    def get_next_small_pixel(self, file: bytes, pixel_size):
        row_number = self.bitmap_info.height - 1
        local_pixel_offset = 0
        pixel_offset = self.header.offset
        while row_number >= 0:
            blue = unpack('B', file[pixel_offset:pixel_offset + 1])[0]
            green = unpack('B', file[pixel_offset + 1:pixel_offset + 2])[0]
            red = unpack('B', file[pixel_offset + 2:pixel_offset + 3])[0]
            x = local_pixel_offset * pixel_size
            y = row_number * pixel_size
            pixel_offset += 3
            yield (x, y), (red, green, blue)
            local_pixel_offset = (local_pixel_offset + 1)
            if local_pixel_offset >= self.bitmap_info.width:
                while (local_pixel_offset * 3) % 4 != 0:
                    local_pixel_offset += 1
                    pixel_offset += 1
                row_number -= 1
                local_pixel_offset = 0

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
