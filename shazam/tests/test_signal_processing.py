from SignalProcessing import *
from exceptions import NotWavData
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


def test_signature_methods():
    spe = SignalProcessorExactMatch(wav1,5)
    spe.compute_spectrogram()
    assert spe.spectrogram == ''' saved comparison spectrogram '''
    spfp = SignalProcessorFreqPeaks(wav1,5)
    spfp.compute_spectrogram()
    assert spfp.spectrogram == ''' saved comparison spectrogram '''
    spfpp = SignalProcessorFreqPowerPairs(wav1,5)
    spfpp.compute_spectrogram()
    assert spfpp.spectrogram == ''' saved comparison spectrogram '''
    sppb= SignalProcessorPowerBands(wav1,5)
    sppb.compute_spectrogram()
    assert sppb.spectrogram == ''' saved comparison spectrogram '''
    spsp =SignalProcessorSmoothedPeriodogram(wav1,5)
    spsp.compute_spectrogram()
    assert spsp.spectrogram == ''' saved comparison spectrogram '''



def test_edge_cases():
    try:
        SignalProcessor('NO DATA')
    except NotWavData:
        pass
    # sp = SignalProcessor(wav1)
    # try:
