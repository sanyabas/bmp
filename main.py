class FileInfo:
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


def open_file(filename):
    with open(filename, 'rb') as file:
        bytestream = []
        for i in file.read():
            bytestream.append(hex(i))
    return bytestream


def check_if_file_is_bmp(file, name):
    if file[:2] != ['0x42', '0x4d']:
        raise TypeError(name + " is not a BMP file")


def get_file_info(file, name):
    size = get_hex_int(file[2:6])
    offset_list = file[10:14]
    offset = get_hex_int(offset_list)
    info_list = file[0xe:0xe + 4]
    version_size = get_hex_int(info_list)
    version = VERSIONS.get(version_size, 'Invalid')
    return FileInfo(name, size, offset, version)


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
