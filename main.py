from struct import unpack


class FileHeader:
    def __init__(self, name='', size=0, offset=0, version=''):
        self.name = name
        self.size = size
        self.offset = offset
        self.version = version

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, number):
        self._size = number

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    def __iter__(self):
        yield "Name: {}".format(self.name)
        yield "Size: {} bytes".format(self.size)
        yield "Offset: {} bytes".format(self.offset)
        yield "Version: {}".format(self.version)


class BitmapInfoCore:
    def __init__(self):
        super().__init__()

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def planes_count(self):
        return self._planes

    @planes_count.setter
    def planes_count(self, value):
        self._planes = value

    @property
    def bit_count(self):
        return self._bit_count

    @bit_count.setter
    def bit_count(self, value):
        self._bit_count = value

    def __iter__(self):
        yield 'Width: {} bytes'.format(self.width)
        yield 'Height: {} bytes'.format(self.height)
        yield 'Planes count: {}'.format(self.planes_count)
        yield 'Bits per pixel: {}'.format(self.bit_count)


class BitmapInfoVersion3(BitmapInfoCore):
    def __init__(self):
        super().__init__()

    @property
    def compression(self):
        return self._compression

    @compression.setter
    def compression(self, value):
        self._compression = value

    @property
    def image_size(self):
        return self._size

    @image_size.setter
    def image_size(self, value):
        self._size = value

    @property
    def x_pixels_per_meter(self):
        return self._ppm_x

    @x_pixels_per_meter.setter
    def x_pixels_per_meter(self, value):
        self._ppm_x = value

    @property
    def y_pixels_per_meter(self):
        return self._ppm_y

    @y_pixels_per_meter.setter
    def y_pixels_per_meter(self, value):
        self._ppm_y = value

    @property
    def color_table_size(self):
        return self._color_table_size

    @color_table_size.setter
    def color_table_size(self, value):
        self._color_table_size = value

    @property
    def important_colors(self):
        return self._important

    @important_colors.setter
    def important_colors(self, value):
        self._important = value

    def __iter__(self):
        for property in super().__iter__():
            yield property
        yield 'Compression type: {}'.format(self.compression)
        yield 'Image data size: {} bytes'.format(self.image_size)
        yield 'Pixels per meter by X: {}'.format(self.x_pixels_per_meter)
        yield 'Pixels per meter by Y: {}'.format(self.y_pixels_per_meter)
        yield 'Size of color table: {} bytes'.format(self.color_table_size)
        yield 'Important colors: {}'.format(self.important_colors)


class BitmapInfoVersion4(BitmapInfoVersion3):
    def __init__(self):
        super().__init__()

    @property
    def red_mask(self):
        return self._red_mask

    @red_mask.setter
    def red_mask(self, value):
        self._red_mask = value

    @property
    def green_mask(self):
        return self._green_mask

    @green_mask.setter
    def green_mask(self, value):
        self._green_mask = value

    @property
    def blue_mask(self):
        return self._blue_mask

    @blue_mask.setter
    def blue_mask(self, value):
        self._blue_mask = value

    @property
    def alpha_mask(self):
        return self._alpha_mask

    @alpha_mask.setter
    def alpha_mask(self, value):
        self._alpha_mask = value

    @property
    def cs_type(self):
        return self._cs_type

    @cs_type.setter
    def cs_type(self, value):
        self._cs_type = value

    @property
    def red_gamma(self):
        return self._red_gamma

    @red_gamma.setter
    def red_gamma(self, value):
        self._red_gamma = value

    @property
    def green_gamma(self):
        return self._green_gamma

    @green_gamma.setter
    def green_gamma(self, value):
        self._green_gamma = value

    @property
    def blue_gamma(self):
        return self._blue_gamma

    @blue_gamma.setter
    def blue_gamma(self, value):
        self._blue_gamma = value

    def __iter__(self):
        for property in super().__iter__():
            yield property
        yield 'Red mask: {0:b}'.format(self.red_mask)
        yield 'Green mask: {0:b}'.format(self.green_mask)
        yield 'Blue mask: {0:b}'.format(self.blue_mask)
        yield 'Alpha mask: {}'.format(self.alpha_mask)
        yield 'Color space type: {}'.format(self.cs_type)


def open_file(filename):
    with open(filename, 'rb') as file:
        return file.read()


def check_if_file_is_bmp(file, name):
    if file[:2] != b'\x42\x4d':
        raise TypeError(name + " is not a BMP file")


def read_file_header(file, name):
    size = unpack('<I', file[0x2:0x6])[0]
    offset = unpack('<I', file[0xa:0xa + 4])[0]
    version_size = unpack('<I', file[0xe:0xe + 4])[0]
    version = VERSIONS.get(version_size, 'Invalid')
    return FileHeader(name, size, offset, version)


def get_bitmap_info(file, header):
    return VERSION_FUNCTIONS.get(header.version)(file)


def fill_core_info(file):
    info = BitmapInfoCore()
    info.version = 'CORE'
    info.width = unpack('<H', file[0x12:0x12 + 2])[0]
    info.height = unpack('<H', file[0x14:0x14 + 2])[0]
    info.planes_count = unpack('<H', file[0x16:0x16 + 2])[0]
    info.bit_count = unpack('<H', file[0x18:0x18 + 2])[0]
    return info


def fill_v3_info(file, info=None):
    if info is None:
        info = BitmapInfoVersion3()
        info.version = 3
    info.width = unpack('<i', file[0x12:0x12 + 4])[0]
    info.height = unpack('<i', file[0x16:0x16 + 4])[0]
    info.planes_count = unpack('<H', file[0x1a:0x1a + 2])[0]
    info.bit_count = unpack('<H', file[0x1c:0x1c + 2])[0]
    info.compression = unpack('<I', file[0x1e:0x1e + 4])[0]
    info.image_size = unpack('<I', file[0x22:0x22 + 4])[0]
    info.x_pixels_per_meter = unpack('<I', file[0x26:0x26 + 4])[0]
    info.y_pixels_per_meter = unpack('<I', file[0x2a:0x2a + 4])[0]
    info.color_table_size = unpack('<I', file[0x2e:0x2e + 4])[0]
    info.important_colors = unpack('<I', file[0x32:0x32 + 4])[0]
    return info


def fill_v4_info(file):
    info = BitmapInfoVersion4()
    info = fill_v3_info(file, info)
    info.version = 4
    info.red_mask = unpack('<I', file[0x36:0x36 + 4])[0]
    info.green_mask = unpack('<I', file[0x3a:0x3a + 4])[0]
    info.blue_mask = unpack('<I', file[0x3e:0x3e + 4])[0]
    info.alpha_mask = unpack('<I', file[0x42:0x42 + 4])[0]
    info.cs_type = unpack('<I', file[0x46:0x46 + 4])[0]
    info.cs_type = unpack('<I', file[0x46:0x46 + 4])[0]
    return info


def get_hex_int(input_list):
    number = 0
    for i in input_list[::-1]:
        number = number * 256 + int(i, 16)
    return number


VERSIONS = {
    12: 'CORE',
    40: 3,
    108: 4,
    124: 5
}

VERSION_FUNCTIONS = {
    'CORE': fill_core_info,
    3: fill_v3_info,
    4: fill_v4_info
}
