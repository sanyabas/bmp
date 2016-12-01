import unittest
import main as parser


class TestFileParsing(unittest.TestCase):
    def setUp(self):
        self.file_name = 'qwe.bmp'
        self.file = parser.open_file(self.file_name)

    def test_bmp_check(self):
        self.assert_file(parser.open_file('aa.bmp'))
        with self.assertRaises(TypeError):
            self.assert_file(parser.open_file('bb.png'))

    def assert_file(self, file):
        parser.check_if_file_is_bmp(file, '')

    def test_header_parsing(self):
        expected = parser.FileHeader(self.file_name, 768122, 122, 4)
        result = parser.read_file_header(parser.open_file(self.file_name), self.file_name)
        self.assertEquals(result, expected)

    def test_core_info_parsing(self):
        expected = parser.BitmapInfoCore()
        expected.bit_count = 24
        expected.height = 400
        expected.width = 640
        result = parser.fill_core_info(self.file)
        self.assertTrue(
            result.bit_count == expected.bit_count and result.height == expected.height and result.width == expected.width)

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
        expected.red_mask = 1934772034
        expected.green_mask = 0
        expected.blue_mask = 0
        expected.alpha_mask = 0
        expected.cs_type = 0
        result = parser.fill_v4_info(self.file)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
