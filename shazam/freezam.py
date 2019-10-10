import sys
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Freezam is a python based audio feature identifier. It tries to identify the song from which '
                    'a short audio segment comes'
        )

    sp_add = parser.add_subparsers(title='add')
    add = sp_add.add_parser('add')
    add.add_argument('--title', type=str)
    add.add_argument('--artist', type=str)

    sp_id = parser.add_subparsers(title='identify')
    identify = sp_id.add_parser('identify')
    identify.add_argument('song', type=argparse.FileType('rb'))

    sp_list = parser.add_subparsers(title='list')
    list_db = sp_list.add_parser('list')

    args = parser.parse_args()

