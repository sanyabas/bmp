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
        self.qp = QPainter()

    def paintEvent(self, e):
        self.qp.begin(self)
        if max(self.bitmap_info.width, self.bitmap_info.height) < self.min_size:
            self.render_picture(self.qp, self.file, self.min_size / self.bitmap_info.width)
        else:
            self.render_picture(self.qp, self.file, 1)
        self.qp.end()

    def render_picture(self, qp: QPainter, file, pixel_size):
        geom = qp.viewport() if self.qp.viewport() else self.qp.window()
        qp.translate((geom.width() - self.bitmap_info.width)/2, (geom.height() - self.bitmap_info.height) /2)
        for pixel in self.get_24_bit_pixels(file, pixel_size):
            coord, color = pixel
            qp.setPen(QColor(*color))
            qp.setBrush(QColor(*color))
            qp.drawRect(*coord, pixel_size, pixel_size)

    def get_24_bit_pixels(self, file: bytes, pixel_size):
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
            local_pixel_offset += 1
            if local_pixel_offset >= self.bitmap_info.width:
                while (local_pixel_offset * 3) % 4 != 0:
                    local_pixel_offset += 1
                    pixel_offset += 1
                row_number -= 1
                local_pixel_offset = 0
