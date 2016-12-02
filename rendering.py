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
        self.byte_count = bitmap_info.bit_count / 8

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        if max(self.bitmap_info.width, self.bitmap_info.height) < self.min_size:
            self.render_picture(qp, self.file, self.min_size / self.bitmap_info.width)
        else:
            self.render_picture(qp, self.file, 1)
        qp.end()

    def render_picture(self, qp: QPainter, file, pixel_size):
        geom = qp.viewport() if qp.viewport() else qp.window()
        qp.translate((geom.width() - self.bitmap_info.width) / 2, (geom.height() - self.bitmap_info.height) / 2)
        for pixel in self.get_24_bit_pixels(file, pixel_size):
            coord, color = pixel
            qp.fillRect(*coord, pixel_size, pixel_size, QColor(*color))

    def get_24_bit_pixels(self, file: bytes, pixel_size):
        row_number = self.bitmap_info.height - 1
        local_pixel_offset = 0
        pixel_offset = self.header.offset
        while row_number >= 0:
            color, pixel_offset = self.get_pixel_color(file, pixel_offset)
            x = local_pixel_offset * pixel_size
            y = row_number * pixel_size
            yield (x, y), color
            local_pixel_offset += 1
            if local_pixel_offset >= self.bitmap_info.width:
                while (local_pixel_offset * self.byte_count) % 4 != 0:
                    local_pixel_offset += 1
                    pixel_offset += 1
                row_number -= 1
                local_pixel_offset = 0

    def get_pixel_color(self, file, offset):
        if self.bitmap_info.bit_count == 24:
            return self.get_24_bit_color(file, offset)
        else:
            return self.get_32_bit_color(file, offset)

    def get_24_bit_color(self, file, offset):
        blue = unpack('B', file[offset:offset + 1])[0]
        green = unpack('B', file[offset + 1:offset + 2])[0]
        red = unpack('B', file[offset + 2:offset + 3])[0]
        return (red, green, blue), offset + 3

    def get_32_bit_color(self, file, offset):
        color = unpack('<I', file[offset:offset + 4])[0]
        red_bin = '{:b}'.format(self.bitmap_info.red_mask & color)
        red = int(red_bin.strip('0'), 2) if red_bin != '0' else 0
        green_bin = '{:b}'.format(self.bitmap_info.green_mask & color)
        green = int(green_bin.strip('0'), 2) if green_bin != '0' else 0
        blue_bin = '{:b}'.format(self.bitmap_info.blue_mask & color)
        blue = int(blue_bin.strip('0'), 2) if blue_bin != '0' else 0
        alpha_bin = '{:b}'.format(self.bitmap_info.alpha_mask & color)
        alpha = int(alpha_bin.strip('0'), 2) if alpha_bin != '0' else 0
        if '{:b}'.format(self.bitmap_info.alpha_mask).strip('0') == '':
            alpha = 255
        return (red, green, blue, alpha), offset + 4
