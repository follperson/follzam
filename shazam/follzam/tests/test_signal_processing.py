from follzam.SignalProcessing import *
from follzam.IO_methods import ReadAudioData
from follzam import basepath
from follzam.database_management import DatabaseHandler
import os
# make sure spectrograms are not negative test


def test_signature_generates():
    rad = ReadAudioData(os.path.join(basepath, r'assets/audio/Blonde Redhead/Barragan/10  - Seven Two.mp3'))
    dbh = DatabaseHandler()
    sp_base = SignalProcessor(rad.array, rad.audio.frame_rate)
    sp_base.compute_spectrogram()
    try:
        sp_base.compute_signature()
    except NotImplementedError as good:
        pass
    try:
        sp_base.match(dbh)
    except NotImplementedError as good:
        pass
    sp_base.compute_spectrogram()
    assert sp_base.spectrogram is not None
    sp_spect = SignalProcessorSpectrogram(rad.array, rad.audio.frame_rate)
    f,t,sxx = sp_spect.compute_spectrogram()
    assert sp_spect.spectrogram is not None
    assert NFFT + 1 == len(f)
    assert rad.audio.frame_rate / 2 == f.max()

    sp_spect.compute_signature()

    assert sp_spect.signature is not None


