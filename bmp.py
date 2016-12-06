import argparse
from sys import argv

from PyQt5.QtWidgets import QApplication

from bmp_core import *
from gui import *


def specify_filename():
    name = input("Specify file name: ")
    while name == '':
        name = input("Specify file name: ")
    return name


def main():
    try:
        args = parse_args()
        if args.gui:
            run_gui(args.file)
        else:
            if args.file is None:
                filename = specify_filename()
            else:
                filename = args.file
            run_console_mode(filename)
    except Exception as e:
        print("Error: " + str(e))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="enable gui")
    parser.add_argument("-f", "--file", help="file to extract")
    return parser.parse_args()


def run_gui(filename):
    app = QApplication(argv)
    widget = MainWidget(filename)
    widget.show()
    app.exec_()


def run_console_mode(filename):
    file = open_file(filename)
    check_if_file_is_bmp(file, filename)
    header = read_file_header(file, filename)
    bitmap_info=get_bitmap_info(file, header)
    print_info(header)
    print_info(bitmap_info)
    extract_palette(file, bitmap_info)


def print_info(info):
    for prop in info:
        print(*prop)


if __name__ == '__main__':
    main()
