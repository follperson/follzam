from follzam.IO_methods import ReadAudioData
from follzam.exceptions import UnsupportedFileType
ex = r'assets/music/Blonde Redhead/Barragán/04  - Cat On Tin Roof.mp3'
ex_url = "https://upload.wikimedia.org/wikipedia/en/0/0c/She_Loves_You_%28Beatles_song_-_sample%29.ogg"
ex_test = r'C:\Users\follm\Documents\s750\assignments-follperson\shazam\assets\files_for_tests\01 Speed Trials_4.mp3'
ex_test_2 = r'C:\Users\follm\Documents\s750\assignments-follperson\shazam\assets\files_for_tests\01 Speed Trials_5.mp3'
ex_test_full = r'C:\Users\follm\Documents\s750\assignments-follperson/assets/audio/songs/01 Speed Trials.mp3'


path_to_mp3 = '/path/to/mp3'
path_to_flac = '/path/to/flac'
path_to_mp4 = '/path/to/mp4'
path_to_wav = '/path/to/wav'
path_to_ogg = '/path/to/ogg'
path_to_non_file = '/fakepath'
path_to_non_audio_file = '/path/to/non-audio-file'
path_to_corrupt_file = '/path/to/corrupt-file'

def test_read_mp3():
    obj = ReadAudioData(filepath=path_to_mp3)
    assert obj.array is not None


def test_read_flac():
    obj = ReadAudioData(filepath=path_to_flac)
    assert obj.array is not None


def test_read_mp4():
    obj = ReadAudioData(filepath=path_to_mp4)
    assert obj.array is not None


def test_read_wav():
    obj = ReadAudioData(filepath=path_to_wav)
    assert obj.array is not None


def test_read_ogg():
    obj = ReadAudioData(filepath=path_to_ogg)
    assert obj.array is not None


def test_read_non_audio_file():
    try:
        ReadAudioData(filepath=path_to_non_audio_file)
    except UnsupportedFileType as ok:
        pass


def test_read_corrupt_file():
    try:
        ReadAudioData(filepath=path_to_corrupt_file)
    except UnsupportedFileType as ok:
        pass


def test_read_non_file():
    try:
        ReadAudioData(filepath=path_to_non_file)
    except AssertionError as ok:
        pass
