from struct import unpack


class CompressedBmpRenderer:
    def __init__(self, file, header, bitmap_info, color_table):
        super().__init__()
        self.file = file
        self.header = header
        self.bitmap_info = bitmap_info
        self.color_table = color_table
        self.escape_functions = {
            0: self.next_row,
            1: self.end_rendering,
            2: self.shift
        }

    def render(self, file, size, pixel_size):
        row_number = self.bitmap_info.height - 1
        local_pixel_offset = 0
        pixel_offset = self.header.offset
        while row_number >= 0:
            if pixel_offset % 2 != 0:
                pixel_offset += 1
            first = unpack('B', file[pixel_offset:pixel_offset + 1])[0]
            if first == 0:
                second = unpack('B', file[pixel_offset + 1:pixel_offset + 2])[0]
                if second in self.escape_functions.keys():
                    local_pixel_offset, pixel_offset, row_number = self.escape_functions[second](file,
                                                                                                 row_number,
                                                                                                 local_pixel_offset,
                                                                                                 pixel_offset)
                else:
                    count = second
                    pixels_count = 0
                    for i in range(count):
                        if self.rendering_is_interrupted(local_pixel_offset, self.bitmap_info.width, pixels_count,
                                                         count):
                            break
                        color_index = unpack('B', file[pixel_offset + 2:pixel_offset + 3])[0]
                        colors = self.extract_colors(color_index, size)
                        for index in colors:
                            yield from self.get_color_and_coords(index, local_pixel_offset, pixel_size, row_number)
                            local_pixel_offset += 1
                            pixels_count += 1
                        pixel_offset += 1
                    pixel_offset += 2
            else:
                count = first
                color_index = unpack('B', file[pixel_offset + 1:pixel_offset + 2])[0]
                colors = self.extract_colors(color_index, size)
                pixels_count = 0
                for i in range(count):
                    for index in colors:
                        if self.rendering_is_interrupted(local_pixel_offset, self.bitmap_info.width, pixels_count,
                                                         count):
                            break
                        yield from self.get_color_and_coords(index, local_pixel_offset, pixel_size, row_number)
                        local_pixel_offset += 1
                        pixels_count += 1
                pixel_offset += 2

    def get_color_and_coords(self, index, local_pixel_offset, pixel_size, row_number):
        color = self.color_table[index]
        x = local_pixel_offset * pixel_size
        y = row_number * pixel_size
        yield (x, y), color

    def shift(self, file, row_number, local_pixel_offset, pixel_offset):
        x_offset = unpack('B', file[pixel_offset + 2:pixel_offset + 3])[0]
        y_offset = unpack('B', file[pixel_offset + 3:pixel_offset + 4])[0]
        local_pixel_offset += x_offset
        row_number -= y_offset
        pixel_offset += 4
        return local_pixel_offset, pixel_offset, row_number

    def end_rendering(self, file=None, row_number=None, local_pixel_offset=None, pixel_offset=None):
        raise StopIteration

    def next_row(self, file, row_number, local_pixel_offset, pixel_offset):
        local_pixel_offset = 0
        row_number -= 1
        pixel_offset += 2
        return local_pixel_offset, pixel_offset, row_number

    def extract_colors(self, color_index, size):
        if size == 4:
            higher = color_index >> 4
            lower = color_index & 0x0f
            colors = [higher, lower]
        else:
            colors = [color_index]
        return colors

    def rendering_is_interrupted(self, row_pixels, width, block_pixels, block_size):
        return row_pixels >= width or block_pixels >= block_size
