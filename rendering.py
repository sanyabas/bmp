import math

from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QPixmap
from PyQt5.QtWidgets import QWidget

from bmp_core import *


class BmpRenderer(QWidget):
    def __init__(self, file, header, bitmap_info, color_table, parent=None):
        QWidget.__init__(self, parent)
        self.pixmap_cache = None
        self.has_drawn = False
        self.min_size = 300
        self.bitmap_info = bitmap_info
        self.file = file
        self.header = header
        self.byte_count = bitmap_info.bit_count / 8 if bitmap_info.bit_count >= 8 else 1
        self.color_table = color_table
        self.byte_offset = 0

        self.color_functions = {
            1: self.get_partial_byte_color,
            2: self.get_partial_byte_color,
            4: self.get_partial_byte_color,
            8: self.get_8_bit_color,
            16: self.get_16_bit_color,
            24: self.get_24_bit_color,
            32: self.get_32_bit_color
        }

    def paintEvent(self, e):
        if self.pixmap_cache is not None:
            self.draw_cached_picture()
            return
        self.render_explicitly()
        if not self.has_drawn:
            self.draw_cached_picture()
            self.has_drawn = True

    def draw_cached_picture(self):
        qp = QPainter()
        geom = self.geometry()
        qp.begin(self)
        qp.resetTransform()
        qp.drawPixmap((geom.width() - self.bitmap_info.width) / 2,
                      (geom.height() - self.bitmap_info.height) / 2,
                      self.pixmap_cache)
        qp.end()

    def render_explicitly(self):
        if self.bitmap_info.height > self.min_size:
            cache_height = self.bitmap_info.height
        else:
            cache_height = self.bitmap_info.height * self.min_size / self.bitmap_info.width
        self.pixmap_cache = QPixmap(max(self.min_size, self.bitmap_info.width), cache_height)
        self.pixmap_cache.fill(QtCore.Qt.transparent)
        qp = QPainter()
        qp.begin(self.pixmap_cache)
        if max(self.bitmap_info.width, self.bitmap_info.height) < self.min_size:
            self.render_picture(qp, self.file, math.floor(self.min_size / self.bitmap_info.width))
        else:
            self.render_picture(qp, self.file, 1)
        qp.end()

    def render_picture(self, qp: QPainter, file, pixel_size):
        if self.bitmap_info.bit_count == 16 or self.bitmap_info.bit_count == 32:
            self.init_rendering()
        if self.bitmap_info.compression == 1 or self.bitmap_info.compression == 2:
            pixel_extractor = self.render_compressed_image(file, 0, pixel_size)
        else:
            pixel_extractor = self.get_pixels(file, pixel_size)
        for pixel in pixel_extractor:
            coord, color = pixel
            qp.fillRect(*coord, pixel_size, pixel_size, QColor(*color))

    def init_rendering(self):
        f_string = '{:032b}' if self.bitmap_info.bit_count == 32 else '{:016b}'
        red = f_string.format(self.bitmap_info.red_mask)
        self.red_left, self.red_right = red.find('1'), red.rfind('1')
        green = f_string.format(self.bitmap_info.green_mask)
        self.green_left, self.green_right = green.find('1'), green.rfind('1')
        blue = f_string.format(self.bitmap_info.blue_mask)
        self.blue_left, self.blue_right = blue.find('1'), blue.rfind('1')
        alpha = f_string.format(
            self.bitmap_info.alpha_mask) if self.bitmap_info.alpha_mask <= 2 ** self.bitmap_info.bit_count else '0'
        self.alpha_left, self.alpha_right = alpha.find('1'), alpha.rfind('1')

        red_length = len('{:b}'.format(self.bitmap_info.red_mask).strip('0'))
        green_length = len('{:b}'.format(self.bitmap_info.green_mask).strip('0'))
        blue_length = len('{:b}'.format(self.bitmap_info.blue_mask).strip('0'))
        alpha_length = len('{:b}'.format(self.bitmap_info.alpha_mask).strip('0'))

        red_max = 2 ** red_length - 1
        green_max = 2 ** green_length - 1
        blue_max = 2 ** blue_length - 1
        alpha_max = 2 ** alpha_length - 1

        self.red_factor = 255 / red_max if red_max != 0 else 1
        self.green_factor = 255 / green_max if green_max != 0 else 1
        self.blue_factor = 255 / blue_max if blue_max != 0 else 1
        self.alpha_factor = 255 / alpha_max if alpha_max != 0 else 1

    def get_pixels(self, file: bytes, pixel_size):
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
                total_offset = pixel_offset - self.header.offset
                while total_offset % 4 != 0:
                    local_pixel_offset += 1
                    pixel_offset += 1
                    total_offset += 1
                row_number -= 1
                local_pixel_offset = 0
                self.byte_offset = 0

    def get_pixel_color(self, file, offset):
        return self.color_functions.get(self.bitmap_info.bit_count)(file, offset)

    def get_32_bit_color(self, file, offset):
        color = unpack('<I', file[offset:offset + 4])[0]
        rgb_color = self.transform_color_to_rgb(color)
        return rgb_color, offset + 4

    def get_24_bit_color(self, file, offset):
        blue = unpack('B', file[offset:offset + 1])[0]
        green = unpack('B', file[offset + 1:offset + 2])[0]
        red = unpack('B', file[offset + 2:offset + 3])[0]
        return (red, green, blue), offset + 3

    def get_16_bit_color(self, file, offset):
        color = unpack('<H', file[offset:offset + 2])[0]
        rgb_color = self.transform_color_to_rgb(color)
        return rgb_color, offset + 2

    def get_8_bit_color(self, file, offset):
        color = unpack('B', file[offset:offset + 1])[0]
        rgb_color = self.color_table[color]
        return rgb_color, offset + 1

    def get_partial_byte_color(self, file, offset):
        if self.byte_offset == 8:
            offset += 1
            self.byte_offset = 0
        if self.byte_offset == 0:
            self.current_byte = '{:08b}'.format(unpack('B', file[offset:offset + 1])[0])
        color = int(self.current_byte[self.byte_offset:self.byte_offset + self.bitmap_info.bit_count], 2)
        self.byte_offset += self.bitmap_info.bit_count
        rgb_color = self.color_table[color]
        return rgb_color, offset

    def transform_color_to_rgb(self, color):
        f_string = '{:032b}' if self.bitmap_info.bit_count == 32 else '{:016b}'
        red_bin = f_string.format(color)[self.red_left:self.red_right + 1]
        green_bin = f_string.format(color)[self.green_left:self.green_right + 1]
        blue_bin = f_string.format(color)[self.blue_left:self.blue_right + 1]
        alpha_bin = f_string.format(color)[self.alpha_left:self.alpha_right + 1]
        red = int(red_bin, 2) * self.red_factor
        green = int(green_bin, 2) * self.green_factor
        blue = int(blue_bin, 2) * self.blue_factor
        alpha = int(alpha_bin, 2) * self.alpha_factor if alpha_bin.strip('0') != '' or self.alpha_left != -1 else 255
        return red, green, blue, alpha

    def render_compressed_image(self, file, size, pixel_size):
        row_number = self.bitmap_info.height - 1
        local_pixel_offset = 0
        pixel_offset = self.header.offset
        while row_number >= 0:
            if pixel_offset % 2 != 0:
                pixel_offset += 1
            first = unpack('B', file[pixel_offset:pixel_offset + 1])[0]
            if first == 0:
                second = unpack('B', file[pixel_offset + 1:pixel_offset + 2])[0]
                if second == 0:
                    local_pixel_offset = 0
                    row_number -= 1
                    pixel_offset += 2
                elif second == 1:
                    raise StopIteration
                elif second == 2:
                    x_offset = unpack('B', file[pixel_offset + 2:pixel_offset + 3])[0]
                    y_offset = unpack('B', file[pixel_offset + 3:pixel_offset + 4])[0]
                    local_pixel_offset += x_offset
                    row_number -= y_offset
                    pixel_offset += 4
                else:
                    count = second
                    for i in range(count):
                        color_index = unpack('B', file[pixel_offset + 2 + i:pixel_offset + 3 + i])[0]
                        color = self.color_table[color_index]
                        x = local_pixel_offset * pixel_size
                        y = row_number * pixel_size
                        yield (x, y), color
                        local_pixel_offset += 1
                    pixel_offset += count + 2
            else:
                count = first
                color_index = unpack('B', file[pixel_offset + 1:pixel_offset + 2])[0]
                color = self.color_table[color_index]
                for i in range(count):
                    x = local_pixel_offset * pixel_size
                    y = row_number * pixel_size
                    yield (x, y), color
                    local_pixel_offset += 1
                pixel_offset += 2
