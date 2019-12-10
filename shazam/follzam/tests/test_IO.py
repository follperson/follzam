from follzam import basepath
import os
from follzam.IO_methods import ReadAudioData
from follzam.exceptions import UnsupportedFileType
ex_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/She_Loves_You_%28Beatles_song_-_sample%29.ogg"

path_to_mp3 = os.path.join(basepath, 'assets/audio/Sigur Ros/Agaetis Byrjun/01 - Intro.mp3')
path_to_flac = os.path.join(basepath, 'assets/audio/Brian Eno/Ambient 1 Music For Airports/01 Brian Eno - 1-1.flac')
path_to_non_file = '/fakepath'
path_to_non_audio_file = os.path.join(basepath, 'assets/audio/Blonde Redhead/Barragan/front.jpg')
path_to_corrupt_file = os.path.join(basepath, 'assets/files_for_tests/01 Barragan_15-25_corrupt.mp3')


def test_read_local():
    print(basepath)
    obj = ReadAudioData(path_to_mp3)
    assert obj.array is not None


def test_read_url():
    obj = ReadAudioData(ex_url)
    assert obj.array is not None


def test_read_flac():
    obj = ReadAudioData(path_to_flac)
    assert obj.array is not None



def test_read_non_audio_file():
    try:
        ReadAudioData(path_to_non_audio_file)
    except UnsupportedFileType as ok:
        pass


def test_read_corrupt_file():
    try:
        ReadAudioData(path_to_corrupt_file)
    except UnsupportedFileType as ok:
        pass


def test_read_non_file():
    try:
        ReadAudioData(path_to_non_file)
    except AssertionError as ok:
        pass
