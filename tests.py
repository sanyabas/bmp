import unittest

import bmp_core as parser


class TestFileParsing(unittest.TestCase):
    def setUp(self):
        self.file_name = 'images/qwe.bmp'
        self.file = parser.open_file(self.file_name)

    def test_bmp_check(self):
        self.assert_file(parser.open_file('images/aa.bmp'))
        with self.assertRaises(TypeError):
            self.assert_file(parser.open_file('images/bb.png'))

    def assert_file(self, file):
        parser.check_if_file_is_bmp(file, '')

    def test_header_parsing(self):
        expected = parser.FileHeader(self.file_name, 768122, 122, 4)
        result = parser.read_file_header(parser.open_file(self.file_name), self.file_name)
        self.assertEqual(result, expected)

    def test_v3_info_parser(self):
        expected = parser.BitmapInfoVersion3()
        expected.version = 3
        expected.bit_count = 24
        expected.height = 400
        expected.width = 640
        expected.compression = 0
        expected.image_size = 768000
        expected.x_pixels_per_meter = 2835
        expected.y_pixels_per_meter = 2835
        expected.important_colors = 0
        expected.planes_count = 1
        expected.color_table_size = 0
        result = parser.fill_v3_info(self.file)
        self.assertEqual(expected, result)

    def test_v4_info_parser(self):
        expected = parser.BitmapInfoVersion4
        expected.version = 4
        expected.bit_count = 24
        expected.height = 400
        expected.width = 640
        expected.compression = 0
        expected.image_size = 768000
        expected.x_pixels_per_meter = 2835
        expected.y_pixels_per_meter = 2835
        expected.important_colors = 0
        expected.planes_count = 1
        expected.color_table_size = 0
        expected.red_mask = 1934772034
        expected.green_mask = 0
        expected.blue_mask = 0
        expected.alpha_mask = 0
        expected.cs_type = 0
        result = parser.fill_v4_info(self.file)
        self.assertEqual(expected, result)

    def test_v5_parser(self):
        expected = parser.BitmapInfoVersion5()
        expected.version = 5
        expected.bit_count = 32
        expected.height = 3
        expected.width = 4
        expected.planes_count = 1
        expected.bit_count = 32
        expected.compression = 3
        expected.image_size = 48
        expected.x_pixels_per_meter = 2835
        expected.y_pixels_per_meter = 2835
        expected.color_table_size = 0
        expected.important_colors = 0
        expected.red_mask = 4278190080
        expected.green_mask = 16711680
        expected.blue_mask = 65280
        expected.alpha_mask = 255
        expected.cs_type = 'BGRs'
        expected.intent = 2
        expected.profile_data = 0
        expected.profile_size = 0

        file_name = 'images/32-3.bmp'
        file = parser.open_file(file_name)
        result = parser.fill_v5_info(file)
        self.assertEqual(expected, result)


class PaletteTester(unittest.TestCase):
    def setUp(self):
        self.file_name = 'images/aa.bmp'
        self.file = parser.open_file(self.file_name)
        self.header = parser.read_file_header(self.file, self.file_name)
        self.info = parser.get_bitmap_info(self.file, self.header)
        self.palette = parser.extract_palette(self.file, self.info)

    def test_palette_extracting(self):
        self.assertEqual(256, len(self.palette))

    def test_palette_splitting(self):
        palette = parser.group_palette_by(self.palette, 8)
        self.assertEqual(32, len(palette))


if __name__ == '__main__':
    unittest.main()
