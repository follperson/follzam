from ReadAudio import *

path_to_mp3 = '/path/to/mp3'
path_to_flac = '/path/to/flac'
path_to_mp4 = '/path/to/mp4'
path_to_wav = '/path/to/wav'
path_to_ogg = '/path/to/ogg'
path_to_non_file = '/fakepath'
path_to_non_audio_file = '/path/to/non-audio-file'
path_to_corrupt_file = '/path/to/corrupt-file'

# i suppose I could put these in a dedicated directory

def test_read_mp3():
    obj = ReadAudioData()
    obj.initialize(filepath=path_to_mp3)
    assert obj.wav is not None


def test_read_flac():
    obj = ReadAudioData()
    obj.initialize(filepath=path_to_flac)
    assert obj.wav is not None


def test_read_mp4():
    obj = ReadAudioData()
    obj.initialize(filepath=path_to_mp4)
    assert obj.wav is not None

def test_read_non_audio_file():
    obj = ReadAudioData()
    try:
        obj.initialize(filepath=path_to_non_audio_file)
    except UnsupportedFileType as ok:
        pass


def test_read_corrupt_file():
    obj = ReadAudioData()
    try:
        obj.initialize(filepath=path_to_corrupt_file)
    except UnsupportedFileType as ok:
        pass


def test_read_non_file():
    obj = ReadAudioData()
    try:
        obj.initialize(filepath=path_to_non_file)
    except AssertionError as ok:
        pass

def test_read_wav():
    obj = ReadAudioData()
    obj.initialize(filepath=path_to_wav)
    assert obj.wav is not None

def test_read_ogg():
    obj = ReadAudioData()
    obj.initialize(filepath=path_to_ogg)
    assert obj.wav is not None


