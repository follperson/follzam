from Resources.signal_processing import*
from exceptions import NotWavData, WindowTooBig
import wave
import pickle

filepath1 = 'assets/files_for_tests/test.wav'
wav1 = wave.open(filepath1)

picklepath1 = 'assets/files_for_tests/test.pkl'
pickle1 = pickle.unpack(picklepath1)

filepath2 = 'assets/files_for_tests/test2.wav'
wav2 = wave.open(filepath2)

picklepath2 = 'assets/files_for_tests/test2.pkl'
pickle2 = pickle.unpack(picklepath2)

# make sure spectrograms are not negative test


def test_windowing():

    sp = SignalProcessor(wav1)
    assert sp.windows == []
    sp.windowing(5)
    assert sp.windows == pickle1.sp1.window

    try:
        sp.windowing(99999)
    except WindowTooBig:
        pass


def test_edge_cases():
    try:
        SignalProcessor('NO DATA')
    except NotWavData:
        pass
    # sp = SignalProcessor(wav1)
    # try:
