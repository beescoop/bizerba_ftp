#! python3

"""Create a file that suppress all the product in the scale system.

Autor:
    Rémy Taymans <remytms@gmail.com>
Current Maintainer:
    Rémy Taymans <remytms@gmail.com>
Creation: 02 dec 2018

Usage:
    this_script filename scale_group

    filename: the path to the file that will be created.
    scale_group: the scale group ID.
"""


import argparse


__author__ = "Rémy Taymans"
__copyright__ = "Copyright 2018, Rémy Taymans"
__credits__ = ["Rémy Taymans"]
__license__ = "GPLv3"
__version__ = "0.1"
__maintainer__ = "Rémy Taymans"
__email__ = "remytms@gmail.com"
__status__ = "Development"


def main():
    """Program start here"""
    args = init_parser().parse_args()

    with open(args.filename, 'w', encoding='cp1252') as file:
        for i in range(1, 10000):
            file.write('S#%s#%s\r\n' % (args.scale_group, i))


def init_parser():
    """Initialise the parser"""
    # Arguments (-h/--help is automatically added)
    parser = argparse.ArgumentParser(
        description=("Generate a file containing commands to suppress all the"
                     "products on scale system")
    )
    parser.add_argument('filename',
                        help="path of the file to write in")
    parser.add_argument('scale_group',
                        help="the scale group id")
    return parser


if __name__ == "__main__":
    main()
