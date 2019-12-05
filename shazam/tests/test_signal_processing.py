from follzam.SignalProcessing import *
from follzam.exceptions import NotWavData

# make sure spectrograms are not negative test




def test_edge_cases():
    try:
        SignalProcessor('NO DATA')
    except NotWavData:
        pass
    # sp = SignalProcessor(wav1)
    # try:
