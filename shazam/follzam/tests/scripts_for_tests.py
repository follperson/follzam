"""
    Just some scripts to help out set up things for testing.
"""

import os
from numpy.random import randint
import subprocess


def split_song(filepath, out_file_root):
    filename = os.path.basename(filepath)
    split_filename = filename.split('.')
    for f in os.listdir(out_file_root):
        if '.'.join(split_filename[:-1]) in f:
            return

    for i in [1, 2, 3, 4]:
        current_filename = split_filename.copy()
        current_filename.insert(-1, str(i))
        subprocess.call('ffmpeg -ss {} -t {} -i "{}" "{}"'.format(randint(10 * i, 10*(i+1)), randint(5, 15), filepath,
                                                            os.path.join(out_file_root, '.'.join(current_filename))))


def generate_snippets_from_catalog():
    root_dir = r'C:\Users\follm\Downloads\torrents\audio\The Cure\Seventeen Seconds'
    out_root = r'C:\Users\follm\Documents\s750\assignments-follperson\shazam\assets\files_for_tests\new_files'
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            print('Splitting', f)
            split_song(os.path.join(root, f), out_root)


if __name__ == '__main__':
    generate_snippets_from_catalog()
